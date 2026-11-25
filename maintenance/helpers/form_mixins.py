from typing import Any

from accounts.models import Account
from maintenance.models import Part


class UserPartsQuerysetMixin:
    """Restrict part selection to the current user's personal catalog.

    Apply ownership filtering to prevent forms from accepting parts
    belonging to other users.
    """

    def __init__(self, *args: Any, user: Account, **kwargs: Any) -> None:
        """Initialize the form with parts belonging to the given user."""

        super().__init__(*args, **kwargs)

        self.fields["parts"].queryset = Part.objects.filter(owner_id=user.pk)
