from fastapi import APIRouter, Depends

from app.auth.dependencies import require_student

router = APIRouter(prefix="/student", tags=["student"], dependencies=[Depends(require_student)])


@router.get("/ping")
def ping(user=Depends(require_student)):
    return {"role": user.role}