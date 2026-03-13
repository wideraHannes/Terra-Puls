from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "terra_pulse",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    beat_schedule={
        "fetch-pulse-every-15min": {
            "task": "app.tasks.fetch_pulse.fetch_all_pulse",
            "schedule": crontab(minute="*/15"),
        },
    },
)
