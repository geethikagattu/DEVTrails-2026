import logging
import os

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_AVAILABLE = False
celery_app = None

try:
    from celery import Celery
    celery_app = Celery(
        "shieldrun_tasks",
        broker=REDIS_URL,
        backend=REDIS_URL,
    )
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Asia/Kolkata",
        enable_utc=True,
        task_track_started=True,
        broker_connection_retry_on_startup=False,
    )
    celery_app.autodiscover_tasks(["app"], force=True)
    CELERY_AVAILABLE = True
    logger.info("✅ Celery connected to Redis")
except Exception as e:
    logger.warning(f"⚠️  Celery/Redis not available ({e}). Running in SYNC mode.")
    # Create a dummy celery_app stub for import compatibility
    class _SyncCeleryStub:
        """Fallback stub when Redis is unavailable. Runs tasks synchronously."""
        def task(self, *args, **kwargs):
            def decorator(fn):
                fn.delay = fn  # .delay() just calls fn directly
                fn.apply_async = lambda args=(), kwargs={}: fn(*args, **kwargs)
                return fn
            return decorator
    celery_app = _SyncCeleryStub()
