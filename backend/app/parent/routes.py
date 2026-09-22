from fastapi import APIRouter, Depends

from app.auth.dependencies import require_parent

router = APIRouter(prefix="/parent", tags=["parent"], dependencies=[Depends(require_parent)])


@router.get("/ping")
def ping(user=Depends(require_parent)):
    return {"role": user.role}