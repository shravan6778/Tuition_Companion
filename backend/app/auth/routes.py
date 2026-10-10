from fastapi import APIRouter, Depends

from app.auth.admin import is_admin
from app.auth.dependencies import get_current_user
from app.models import User
from app.schemas import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    out = UserOut.model_validate(user)
    out.is_admin = is_admin(user)
    return out