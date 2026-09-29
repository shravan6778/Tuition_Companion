from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def get_session_factory():
    """Lets background tasks open their own session using the same factory the
    request used. Overridden in tests so background work hits the test database."""
    return SessionLocal