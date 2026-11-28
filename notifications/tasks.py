from celery import shared_task

from .services import generate_document_reminders, generate_maintenance_reminders


@shared_task
def check_document_reminders() -> int:
    """Execute the scheduled document reminder generation."""

    return generate_document_reminders()


@shared_task
def check_maintenance_reminders() -> int:
    """Execute the scheduled maintenance reminder generation."""

    return generate_maintenance_reminders()
