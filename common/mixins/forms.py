from typing import Any

from django.http import HttpRequest


class UserFormKwargsMixin:
    """Provide the current user to forms that require user-specific data.

    Allow forms to filter available choices and apply validation rules
    based on the authenticated user.
    """

    request: HttpRequest

    def get_form_kwargs(self) -> dict[str, Any]:
        """Extend the default form arguments with the current authenticated user."""

        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user

        return kwargs
