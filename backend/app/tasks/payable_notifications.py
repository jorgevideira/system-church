from datetime import date, datetime, timezone

from app.tasks.celery_app import celery_app


@celery_app.task(name="payable_notifications.process_due_payable_reminders")
def process_due_payable_reminders(reference_date_iso: str | None = None) -> dict:
    from app.db.session import SessionLocal
    from app.services import payable_notification_service

    db = SessionLocal()
    try:
        reference_date = (
            date.fromisoformat(reference_date_iso)
            if reference_date_iso
            else datetime.now(timezone.utc).date()
        )
        notifications = payable_notification_service.enqueue_due_payable_notifications(
            db,
            reference_date=reference_date,
        )

        sent = 0
        failed = 0
        for notification in notifications:
            payable_notification_service.dispatch_notification(db, notification)
            if notification.status == "sent":
                sent += 1
            elif notification.status == "failed":
                failed += 1

        return {
            "reference_date": reference_date.isoformat(),
            "queued": len(notifications),
            "sent": sent,
            "failed": failed,
        }
    finally:
        db.close()
