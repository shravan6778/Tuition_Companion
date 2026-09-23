from typing import Any, Dict, List, Union

from sqlalchemy import select
from supertokens_python import InputAppInfo, SupertokensConfig, init
from supertokens_python.asyncio import delete_user
from supertokens_python.recipe import emailpassword, session
from supertokens_python.recipe.emailpassword import InputFormField, InputSignUpFeature
from supertokens_python.recipe.emailpassword.interfaces import (
    APIInterface,
    APIOptions,
    SignUpPostOkResult,
)
from supertokens_python.recipe.emailpassword.types import FormField
from supertokens_python.recipe.session.interfaces import SessionContainer
from supertokens_python.types import GeneralErrorResponse

from app.auth.identity import PHONE_RE, USERNAME_RE
from app.core.codes import generate_unique_code
from app.core.config import settings
from app.db.session import SessionLocal
from app.models import Role, User

GENERIC_ERROR = "Could not create account with these details"


def _field(form_fields: List[FormField], field_id: str) -> str:
    return next(f.value for f in form_fields if f.id == field_id)


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

        if role not in (
            Role.teacher.value,
            Role.student.value,
            Role.parent.value,
        ):
            return GeneralErrorResponse(GENERIC_ERROR)

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

                db.add(
                    User(
                        supertokens_user_id=response.user.id,
                        name=name,
                        username=username,
                        phone=phone,
                        role=Role(role),
                        link_code=link_code,
                    )
                )

                db.commit()

            except Exception as exc:
                print("========== SIGNUP DATABASE ERROR ==========")
                print(repr(exc))
                print("============================================")

                db.rollback()
                db.close()
                await delete_user(response.user.id)
                return GeneralErrorResponse(GENERIC_ERROR)

            else:
                db.close()

        return response

    original_implementation.sign_up_post = sign_up_post
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
                sign_up_feature=InputSignUpFeature(
                    form_fields=[
                        InputFormField(id="name"),
                        InputFormField(id="username", validate=validate_username),
                        InputFormField(id="phone", validate=validate_phone),
                        InputFormField(id="role"),
                    ]
                ),
                override=emailpassword.InputOverrideConfig(
                    apis=override_email_password_apis
                ),
            ),
        ],
    )