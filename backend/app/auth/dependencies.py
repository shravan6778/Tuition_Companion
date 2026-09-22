from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

from app.db.session import get_db
from app.models import Role, User

# Defined once at module level so tests can override this exact dependency object.
session_dependency = verify_session()


def get_current_user(
    s: SessionContainer = Depends(session_dependency),
    db: Session = Depends(get_db),
) -> User:
    # Role comes from OUR database on every request, never from the session payload.
    user = db.scalar(select(User).where(User.supertokens_user_id == s.get_user_id()))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
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