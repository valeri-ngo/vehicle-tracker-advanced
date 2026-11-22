from notifications.models import Notification


def build_document_reminder_key(document):
    """Build a unique reminder key using the document ID and expiration date."""
    return f"document:{document.id}:{document.expires_on.isoformat()}:expiry"


def create_document_reminder(document):
    """Create a document expiration reminder if one does not already exist."""

    if not document.reminder_due:
        return None, False

    defaults = {
        "recipient": document.vehicle.owner,
        "notification_type": Notification.NotificationTypes.DOCUMENT,
        "title": f"{document.get_document_type_display()} expiration",
        "message": f"{document.get_document_type_display()} - {document.expires_on.isoformat()}",
        "document": document,
    }

    key = build_document_reminder_key(document)

    Notification(
        **defaults,
        deduplication_key=key,
    ).full_clean(validate_unique=False)

    notification, created = Notification.objects.get_or_create(
        defaults=defaults,
        deduplication_key=key,
    )

    return notification, created
