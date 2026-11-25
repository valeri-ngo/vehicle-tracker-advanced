from typing import Any

from django.core.management.base import BaseCommand

from notifications.services import generate_document_reminders


class Command(BaseCommand):
    """Provide a management command for manual document reminder generation."""

    help = "Generate expiration reminders for vehicle documents."

    def handle(self, *args: Any, **options: Any) -> None:
        """Generate document reminders and report the number created."""

        create_count = generate_document_reminders()

        self.stdout.write(self.style.SUCCESS(f"Generated {create_count} reminder(s)."))
