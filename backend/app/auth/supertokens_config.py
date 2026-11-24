import logging
import math
from typing import Any, Dict, List, Union

from sqlalchemy import select
from supertokens_python import InputAppInfo, SupertokensConfig, init
from supertokens_python.asyncio import delete_user
from supertokens_python.recipe import emailpassword, session
from supertokens_python.recipe.emailpassword import InputFormField, InputSignUpFeature
from supertokens_python.recipe.emailpassword.interfaces import (
    APIInterface,
    APIOptions,
    SignInPostOkResult,
    SignUpPostOkResult,
    WrongCredentialsError,
)
from supertokens_python.recipe.emailpassword.types import FormField
from supertokens_python.recipe.session.interfaces import SessionContainer
from supertokens_python.types import GeneralErrorResponse

from app import audit
from app.auth import invites
from app.auth.identity import PHONE_RE, USERNAME_RE
from app.core.codes import generate_unique_code
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import SessionLocal
from app.models import AccountStatus, Role, User

logger = logging.getLogger(__name__)

GENERIC_ERROR = "Could not create account with these details"
INVITE_ERROR = "This invite code is not valid, has expired or was already used"
INVITE_ONLY_ERROR = "Teacher accounts are by invitation only. Ask your administrator for an invite code."
DISABLED_ERROR = "This account has been disabled. Please contact your administrator."
LOGIN_BUCKET = "login-failures"


def _field(form_fields: List[FormField], field_id: str) -> str:
    return next(f.value for f in form_fields if f.id == field_id)


def _optional_field(form_fields: List[FormField], field_id: str) -> str:
    return next((str(f.value or "") for f in form_fields if f.id == field_id), "")


def _login_key(email: str) -> str:
    """The username part of the hidden login email (auth/identity.py: username_to_email)."""
    return email.strip().lower().rsplit("@", 1)[0][:64]


async def validate_username(value: str, tenant_id: str):
    if not USERNAME_RE.match(value):
        return "Username must be 3-30 characters: lowercase letters, numbers, underscore only"
    return None


async def validate_phone(value: str, sign_up_posttenant_id: str):
    if not PHONE_RE.match(value.replace(" ", "").replace("-", "")):
        return "Enter a valid phone number"
    return None


def override_email_password_apis(original_implementation: APIInterface) -> APIInterface:
    original_sign_up_post = original_implementation.sign_up_post
    original_sign_in_post = original_implementation.sign_in_post

    async def sign_up_post(
        form_fields: List[FormField],
        tenant_id: str,
        session: Union[SessionContainer, None],
        should_try_linking_with_session_user: Union[bool, None],
        api_options: APIOptions,
        user_context: Dict[str, Any],
    ):
        name = _field(form_fields, "name")
        username = _field(form_fields, "username")
        phone = _field(form_fields, "phone")
        role = _field(form_fields, "role")
        invite_code = _optional_field(form_fields, "invite_code")

        if role not in (
            Role.teacher.value,
            Role.student.value,
            Role.parent.value,
        ):
            return GeneralErrorResponse(GENERIC_ERROR)

        # Who may become a teacher is decided BEFORE the identity is created (anyone on a public URL could
        # otherwise register as a teacher and spend the AI quota). A valid invite activates the account at once;
        # without one the account waits for an administrator ("approval") or is refused ("invite").
        account_status = AccountStatus.ACTIVE
        invite_id = None
        if role == Role.teacher.value:
            db = SessionLocal()
            try:
                invite = invites.find_active(db, invite_code) if invite_code.strip() else None
                invite_id = invite.id if invite is not None else None
            finally:
                db.close()
            if invite_code.strip() and invite_id is None:
                return GeneralErrorResponse(INVITE_ERROR)
            if invite_id is None:
                mode = settings.teacher_signup_mode.lower()
                if mode == "invite":
                    return GeneralErrorResponse(INVITE_ONLY_ERROR)
                if mode != "open":
                    account_status = AccountStatus.PENDING

        # SuperTokens creates the identity here.
        # The frontend maps username to a hidden synthetic email,
        # so duplicate usernames are rejected by SuperTokens.
        response = await original_sign_up_post(
            form_fields,
            tenant_id,
            session,
            should_try_linking_with_session_user,
            api_options,
            user_context,
        )

        if isinstance(response, SignUpPostOkResult):
            db = SessionLocal()

            try:
                link_code = None

                if role == Role.student.value:
                    link_code = generate_unique_code(
                        lambda c: db.scalar(
                            select(User.id).where(User.link_code == c)
                        )
                        is not None,
                        length=8,
                    )
                #username replaces phone as the unique login identifier
                user = User(
                    supertokens_user_id=response.user.id,
                    name=name,
                    username=username,
                    phone=phone,
                    role=Role(role),
                    link_code=link_code,
                    status=account_status,
                )
                db.add(user)
                db.flush()
                if invite_id is not None and not invites.consume(db, invite_id, user.id):
                    raise ValueError("invite was used by someone else in the meantime")  # same code, two signups
                audit.record(db, "user.signup", target_type="user", target_id=user.id, target_label=username,
                             detail={"role": role, "status": account_status, "invite": invite_id is not None})
                db.commit()

            except Exception as exc:
                # No print(): this goes to the log with the request id. Only the error's type and the database's own
                # message are logged, never the statement's parameters (they hold the person's name and phone).
                reason = str(getattr(exc, "orig", exc)).splitlines()[0][:200] if str(getattr(exc, "orig", exc)) else ""
                logger.error("Signup could not save the account for username=%s role=%s: %s: %s",
                             username, role, type(exc).__name__, reason)

                db.rollback()
                db.close()
                await delete_user(response.user.id)
                if invite_id is not None:
                    return GeneralErrorResponse(INVITE_ERROR)
                return GeneralErrorResponse(GENERIC_ERROR)

            else:
                db.close()

        return response

    async def sign_in_post(
        form_fields: List[FormField],
        tenant_id: str,
        session: Union[SessionContainer, None],
        should_try_linking_with_session_user: Union[bool, None],
        api_options: APIOptions,
        user_context: Dict[str, Any],
    ):
        # Lock a USERNAME after too many failed attempts (it holds for an unknown username as well, so it tells
        # an attacker nothing about which usernames exist).
        key = _login_key(_optional_field(form_fields, "email"))
        wait = limiter.retry_after(LOGIN_BUCKET, key, settings.login_max_failures, settings.login_window_s)
        if wait:
            logger.warning("Login refused: username=%s is locked for %ss", key, wait)
            return GeneralErrorResponse(f"Too many failed login attempts. Try again in {max(1, math.ceil(wait / 60))} minute(s).")

        response = await original_sign_in_post(
            form_fields, tenant_id, session, should_try_linking_with_session_user, api_options, user_context)

        if isinstance(response, WrongCredentialsError):
            limiter.record(LOGIN_BUCKET, key)
            if limiter.retry_after(LOGIN_BUCKET, key, settings.login_max_failures, settings.login_window_s):
                logger.warning("Username=%s locked after %s failed logins", key, settings.login_max_failures)
                audit.record_now("auth.login_locked", target_type="user", target_label=key, session_factory=SessionLocal,
                                 detail={"failures": settings.login_max_failures, "window_s": settings.login_window_s})
        elif isinstance(response, SignInPostOkResult):
            limiter.clear(LOGIN_BUCKET, key)
            # A disabled account gets no new session (get_current_user would refuse it anyway; this says why).
            db = SessionLocal()
            try:
                disabled = db.scalar(select(User.id).where(
                    User.supertokens_user_id == response.user.id, User.status == AccountStatus.DISABLED)) is not None
            finally:
                db.close()
            if disabled:
                await response.session.revoke_session()
                return GeneralErrorResponse(DISABLED_ERROR)
        return response

    original_implementation.sign_up_post = sign_up_post
    original_implementation.sign_in_post = sign_in_post
    return original_implementation


def init_supertokens() -> None:
    init(
        app_info=InputAppInfo(
            app_name=settings.app_name,
            api_domain=settings.api_domain,
            website_domain=settings.website_domain,
            api_base_path="/auth",
        ),
        supertokens_config=SupertokensConfig(
            connection_uri=settings.supertokens_connection_uri,
            api_key=settings.supertokens_api_key,
        ),
        framework="fastapi",
        mode="asgi",
        recipe_list=[
            session.init(),
            emailpassword.init(
                #username replaces phone as the unique login identifier
                sign_up_feature=InputSignUpFeature(
                    form_fields=[
                        InputFormField(id="name"),
                        InputFormField(id="username", validate=validate_username),
                        InputFormField(id="phone", validate=validate_phone),
                        InputFormField(id="role"),
                        InputFormField(id="invite_code", optional=True),  # teachers only; see TEACHER_SIGNUP_MODE
                    ]
                ),
                override=emailpassword.InputOverrideConfig(
                    apis=override_email_password_apis
                ),
            ),
        ],
    )