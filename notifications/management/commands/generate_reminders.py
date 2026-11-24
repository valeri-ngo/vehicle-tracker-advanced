from django.core.management.base import BaseCommand
from django.utils import timezone

from documents.models import VehicleDocument
from notifications.services import create_document_reminder


class Command(BaseCommand):
    help = "Generate expiration reminders for vehicle documents."

    def handle(self, *args, **options):
        documents = VehicleDocument.objects.filter(
            notifications_enabled=True,
            expires_on__gte=timezone.localdate(),
        ).select_related("vehicle__owner")

        create_count = 0

        for document in documents.iterator():
            _, created = create_document_reminder(document)

            if created:
                create_count += 1

        self.stdout.write(self.style.SUCCESS(f"Generated {create_count} reminder(s)."))
