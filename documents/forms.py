from typing import Any, ClassVar

from django import forms

from accounts.models import Account
from documents.models import VehicleDocument


class VehicleDocumentForm(forms.ModelForm):
    """Handle the creation and editing of vehicle document metadata.

    Allow users to specify expiration dates, reminder preferences
    and additional notes without uploading actual documents.
    """

    class Meta:
        model = VehicleDocument

        fields = (
            "document_type",
            "expires_on",
            "reminder_days_before",
            "notifications_enabled",
            "notes",
        )

        widgets: ClassVar[dict[str, forms.Widget]] = {
            "expires_on": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
        }

    def __init__(self, *args: Any, user: Account, **kwargs: Any) -> None:
        """Initialize the form according to the user's reminder permissions."""
        super().__init__(*args, **kwargs)

        can_customize_reminders: bool = user.has_perm(
            "documents.customize_document_reminders"
        )

        if not can_customize_reminders:
            self.fields["reminder_days_before"].disabled = True
            self.initial["reminder_days_before"] = 7
