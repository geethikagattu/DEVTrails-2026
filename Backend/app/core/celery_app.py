from celery import Celery
from app.core.config import REDIS_URL

# Create the celery instance
celery_app = Celery(
    "shieldrun_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# Additional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
)

# Autodiscover tasks from the app
celery_app.autodiscover_tasks(["app"], force=True)
