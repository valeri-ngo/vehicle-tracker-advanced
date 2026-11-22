from typing import ClassVar

from django import forms

from documents.models import VehicleDocument


class VehicleDocumentForm(forms.ModelForm):
    class Meta:
        model = VehicleDocument

        fields = (
            "document_type",
            "expires_on",
            "reminder_days_before",
            "notifications_enabled",
            "notes",
        )

        widgets: ClassVar[dict[str, forms.DateInput]] = {
            "expires_on": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
        }
