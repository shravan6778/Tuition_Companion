from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

from app.core import requestctx
from app.db.session import get_db
from app.models import AccountStatus, Role, User

# Defined once at module level so tests can override this exact dependency object.
session_dependency = verify_session()


def get_user_any_status(
    s: SessionContainer = Depends(session_dependency),
    db: Session = Depends(get_db),
) -> User:
    """The signed-in user whatever their account status (only /auth/me needs this: a teacher who is still
    waiting for approval must be able to see that message). Everything else uses get_current_user."""
    # Role comes from OUR database on every request, never from the session payload.
    user = db.scalar(select(User).where(User.supertokens_user_id == s.get_user_id()))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    requestctx.set_user(user.id, user.username, user.role)
    if user.status == AccountStatus.DISABLED:
        # Checked on every request, so a disabled account is locked out at once, even though its already-issued
        # access token stays cryptographically valid until it expires (SuperTokens does not look in the database).
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This account has been disabled. Please contact your administrator.")
    return user


def get_current_user(user: User = Depends(get_user_any_status)) -> User:
    if user.status == AccountStatus.PENDING:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Your account is waiting for approval by an administrator.")
    return user


def require_roles(*roles: Role):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")
        return user

    return checker


require_teacher = require_roles(Role.teacher)
require_student = require_roles(Role.student)
require_parent = require_roles(Role.parent)
