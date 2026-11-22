from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError

from .models import Account


class AccountRegistrationForm(UserCreationForm):
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

    def clean_email(self):
        email = self.cleaned_data["email"]

        email_exists = Account.objects.filter(email__iexact=email).exists()

        if email_exists:
            raise ValidationError("This email is already in use.")

        return email
