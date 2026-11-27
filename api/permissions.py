from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from accounts.models import Account
from common.quotas import get_subscription_plan


class HasVIPSubscription(BasePermission):
    """Restrict API access to VIP subscribers and superusers."""

    message = "API access requires a VIP subscription."

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Determine whether the authenticated user has premium API access."""

        if not request.user.is_authenticated:
            return False

        user = request.user
        if not isinstance(user, Account):
            return False

        plan = get_subscription_plan(user)

        return plan in ("VIP", "Superuser")
