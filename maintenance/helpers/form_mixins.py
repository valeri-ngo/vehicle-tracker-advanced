from typing import Any

from accounts.models import Account
from maintenance.helpers.querysets import filter_available_maintenance_items


class MaintenanceItemQuerysetMixin:
    """Restrict maintenance item selection to standard and user-owned items.

    Allow users to select predefined maintenance items and their own
    custom items while preventing access to items owned by other users.
    """

    def __init__(self, *args: Any, user: Account, **kwargs: Any) -> None:
        """Initialize the form with maintenance items available to the user."""

        super().__init__(*args, **kwargs)

        queryset = self.fields["maintenance_items"].queryset

        self.fields["maintenance_items"].queryset = filter_available_maintenance_items(
            queryset, user
        )
