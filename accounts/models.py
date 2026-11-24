from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower


class Account(AbstractUser):
    phone_number = models.CharField(
        max_length=20,
        blank=True,
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                Lower("email"),
                condition=~models.Q(email=""),
                name="unique_account_email_case_insensitive",
            ),
        )
