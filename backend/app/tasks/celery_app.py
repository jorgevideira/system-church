from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "church_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.process_statement",
        "app.tasks.event_notifications",
        "app.tasks.payable_notifications",
    ],
)
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "payable-reminders-daily": {
        "task": "payable_notifications.process_due_payable_reminders",
        "schedule": crontab(hour=10, minute=0),
    },
}
celery_app.autodiscover_tasks(["app.tasks"])
