from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from supertokens_python import get_all_cors_headers
from supertokens_python.framework.fastapi import get_middleware

from app.admin.routes import router as admin_router
from app.assessment.routes import mastery_router, router as check_router
from app.assignments import manual as manual_tasks
from app.assignments.routes import student_router as assignment_student_router, teacher_router as assignment_teacher_router
from app.auth.routes import router as auth_router
from app.auth.supertokens_config import init_supertokens
from app.core.config import settings
from app.core.errors import ProcessingError, QuotaExceededError
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware
from app.core.startup import validate_runtime_config
from app.doubts.routes import router as doubt_router
from app.parent.routes import router as parent_router
from app.student.routes import router as student_router
from app.student.content_routes import router as student_content_router
from app.teacher.routes import router as teacher_router
from app.assessment.quiz_routes import student_practice_router, student_quiz_router, teacher_quiz_router
from app.assessment.review import router as review_router
from app.speech.routes import router as speech_router
from app.teacher import routes as teacher_routes
from app.teacher import student_routes as teacher_student_routes

setup_logging()
validate_runtime_config()  # refuses to start a non-dev server with an unsafe configuration (core/startup.py)
init_supertokens()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from app.monitoring.health import start_heartbeat, stop_heartbeat

    start_heartbeat()  # only when UPTIME_PING_URL is set
    yield
    stop_heartbeat()


app = FastAPI(title="Tuition Companion API", lifespan=lifespan)

# get_middleware must be added before CORSMiddleware, so CORS ends up
# as the outer layer and handles preflight before SuperTokens sees the request.
app.add_middleware(get_middleware())
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type"] + get_all_cors_headers(),
    expose_headers=["X-Request-ID"],
)
# Outermost: gives every request an id (also on CORS preflights and errors), logs it and counts it for the status page.
app.add_middleware(RequestContextMiddleware)


@app.exception_handler(QuotaExceededError)
def quota_exceeded_handler(request: Request, exc: QuotaExceededError):
    # Before ProcessingError's handler (this is a subclass): a cap is "try later" (429), the kill switch "paused" (503).
    headers = {"Retry-After": str(exc.retry_after)} if exc.retry_after else None
    return JSONResponse(status_code=503 if exc.kind == "kill_switch" else 429, headers=headers,
                        content={"detail": str(exc), "code": f"ai_{exc.kind}"})


@app.exception_handler(ProcessingError)
def processing_error_handler(request: Request, exc: ProcessingError):
    # ProcessingError messages are written to be safe to show to the teacher.
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready():
    """For an external uptime monitor (UptimeRobot, Better Stack...): 200 only while the database answers. No details."""
    from app.db.session import SessionLocal
    from app.monitoring.health import check_database

    db = SessionLocal()
    try:
        ok = check_database(db)["ok"]
    finally:
        db.close()
    return JSONResponse(status_code=200 if ok else 503, content={"status": "ok" if ok else "unavailable"})


app.include_router(auth_router)
app.include_router(teacher_router)
app.include_router(assignment_teacher_router)
app.include_router(teacher_routes.router)
app.include_router(teacher_student_routes.router)
app.include_router(admin_router)
app.include_router(student_router)
app.include_router(student_content_router)
app.include_router(assignment_student_router)
app.include_router(manual_tasks.teacher_router)
app.include_router(manual_tasks.student_router)
app.include_router(doubt_router)
app.include_router(check_router)
app.include_router(mastery_router)
app.include_router(teacher_quiz_router)
app.include_router(student_quiz_router)
app.include_router(student_practice_router)
app.include_router(review_router)
app.include_router(speech_router)
app.include_router(parent_router)
