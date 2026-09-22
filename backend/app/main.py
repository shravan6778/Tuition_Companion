from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supertokens_python import get_all_cors_headers
from supertokens_python.framework.fastapi import get_middleware

from app.auth.routes import router as auth_router
from app.auth.supertokens_config import init_supertokens
from app.core.config import settings
from app.core.logging import setup_logging
from app.parent.routes import router as parent_router
from app.student.routes import router as student_router
from app.teacher.routes import router as teacher_router

setup_logging()
init_supertokens()

app = FastAPI(title="Tuition Companion API")

# get_middleware must be added before CORSMiddleware, so CORS ends up
# as the outer layer and handles preflight before SuperTokens sees the request.
app.add_middleware(get_middleware())
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type"] + get_all_cors_headers(),
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(teacher_router)
app.include_router(student_router)
app.include_router(parent_router)