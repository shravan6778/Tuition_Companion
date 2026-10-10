"""Who may delete OFFICIAL books and chapters: teachers whose username is listed in ADMIN_USERNAMES (empty = nobody)."""
from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.core.config import settings
from app.models import Role, User


def admin_usernames() -> set[str]:
    return {u.strip().lower() for u in settings.admin_usernames.split(",") if u.strip()}


def is_admin(user: User) -> bool:
    return user.role == Role.teacher and (user.username or "").lower() in admin_usernames()


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not is_admin(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only an administrator can change official books")
    return user
