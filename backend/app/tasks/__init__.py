"""Task package imports for Celery auto-discovery."""

from app.tasks.process_statement import process_statement_task

__all__ = ["process_statement_task"]
