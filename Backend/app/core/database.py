from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)
print("USING DB:", DATABASE_URL)
# ─── Session ───────────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ─── Base ──────────────────────────────────────────────────────────────────────
Base = declarative_base()


# ─── Dependency for FastAPI routes ─────────────────────────────────────────────
def get_db():
    """
    FastAPI dependency. Use this in every route:

        @router.get("/something")
        def my_route(db: Session = Depends(get_db)):
            ...

    Opens a DB session, yields it, and ALWAYS closes it after the request,
    even if an exception is raised.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"DB session error: {e}")
        raise
    finally:
        db.close()

def create_tables():
    """
    Creates all tables in the database if they don't exist.
    Called once on app startup.
    """
    from app.models import models  # noqa: import triggers table registration
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified")


def check_db_connection():
    """Health check — returns True if DB is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"DB health check failed: {e}")
        return False
