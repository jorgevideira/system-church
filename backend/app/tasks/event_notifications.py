from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.event_notification import EventNotification
from app.db.session import SessionLocal
from app.services import event_notification_service
from app.tasks.celery_app import celery_app


@celery_app.task(name="event_notifications.dispatch_event_notification")
def dispatch_event_notification(notification_id: int) -> None:
    db: Session = SessionLocal()
    try:
        notification = db.query(EventNotification).filter(EventNotification.id == notification_id).first()
        if notification is None:
            return
        # Only dispatch queued/failed notifications; allow manual retry by requeueing.
        if notification.status not in {"queued", "failed"}:
            return
        event_notification_service.dispatch_notification(db, notification)
    finally:
        db.close()

