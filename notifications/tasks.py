from celery import shared_task

from documents.models import VehicleDocument
from notifications.services import create_document_reminder


@shared_task
def check_document_reminders():
    """Check vehicle documents and create reminders when they are due."""
    documents = VehicleDocument.objects.filter(
        notifications_enabled=True,
    ).select_related("vehicle__owner")

    create_count = 0

    for document in documents:
        _, created = create_document_reminder(document)

        if created:
            create_count += 1

    return create_count
