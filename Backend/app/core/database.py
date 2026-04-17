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

def run_migrations():
    """
    Add any new columns that don't exist yet (safe, idempotent migrations).
    Called on every startup — uses IF NOT EXISTS so it's always safe to re-run.
    """
    migrations = [
        "ALTER TABLE workers ADD COLUMN IF NOT EXISTS zone VARCHAR(50)",
        "ALTER TABLE workers ADD COLUMN IF NOT EXISTS firebase_uid VARCHAR(128)",
        "ALTER TABLE workers ADD COLUMN IF NOT EXISTS zone_risk_score INTEGER DEFAULT 50",
        "ALTER TABLE workers ADD COLUMN IF NOT EXISTS avg_daily_earnings FLOAT DEFAULT 500.0",
        "ALTER TABLE workers ADD COLUMN IF NOT EXISTS upi_id VARCHAR(100)",
    ]
    from sqlalchemy import text
    with engine.begin() as conn:
        for sql in migrations:
            try:
                conn.execute(text(sql))
            except Exception as e:
                logger.warning(f"Migration skipped ({e})")
    logger.info("✅ Schema migrations applied")


def create_tables():
    """
    Creates all tables in the database if they don't exist.
    Called once on app startup.
    """
    from app.models import models  # noqa: import triggers table registration
    Base.metadata.create_all(bind=engine)
    run_migrations()
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
