from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError

from .models import Account


class AccountRegistrationForm(UserCreationForm):
    """Handle account registration with email and password validation.

    Extend Django's built-in registration form with a required email
    address and an optional phone number.
    """

    email = forms.EmailField(
        required=True,
    )

    class Meta(UserCreationForm.Meta):
        model = Account
        fields = (
            "username",
            "email",
            "phone_number",
        )

    def clean_email(self) -> str:
        """Validate email uniqueness regardless of letter case.

        Raise ValidationError if the address is already associated
        with an existing account.
        """

        email = self.cleaned_data["email"]

        email_exists = Account.objects.filter(email__iexact=email).exists()

        if email_exists:
            raise ValidationError("This email is already in use.")

        return email
