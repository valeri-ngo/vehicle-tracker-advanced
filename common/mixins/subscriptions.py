from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse

from common.quotas import get_subscription_limit


class SubscriptionQuotaMixin:
    """Enforce subscription quotas for resource operations."""

    request: HttpRequest
    quota_resource: str | None = None

    def get_quota_queryset(self) -> QuerySet:
        """Return the queryset used to determine the user's current resource usage."""

        raise NotImplementedError

    def get_quota_limit(self) -> int | None:
        """Return the subscription limit for the configured resource."""

        if self.quota_resource is None:
            raise NotImplementedError("quota_resource must be configured.")

        return get_subscription_limit(self.request.user, self.quota_resource)

    def is_quota_exceeded(self) -> bool:
        """Check whether the user has reached the subscription quota."""

        limit = self.get_quota_limit()

        if limit is None:
            return False

        count = self.get_quota_queryset().count()

        return count >= limit

    def should_check_quota(self, form: ModelForm) -> bool:
        """Determine whether the submitted form requires a quota check."""

        return True

    def validate_locked_form(self, form: ModelForm) -> bool:
        """Validate additional business rules while holding the account lock."""

        return True

    def form_valid(self, form: ModelForm) -> HttpResponse:
        """Validate quotas and business rules before saving a resource."""

        with transaction.atomic():
            self._lock_account()

            if not self._validate_quota(form):
                return self.form_invalid(form)

            if not self.validate_locked_form(form):
                return self.form_invalid(form)

            return super().form_valid(form)

    def _lock_account(self) -> None:
        """Lock the current account for quota enforcement."""

        User = get_user_model()

        User.objects.select_for_update().get(
            pk=self.request.user.pk,
        )

    def _validate_quota(self, form: ModelForm) -> bool:
        """Validate the subscription quota."""

        if not self.should_check_quota(form):
            return True

        error = self.get_quota_error()

        if error is None:
            return True

        form.add_error(field=None, error=error)

        return False

    def get_quota_error(self) -> str | None:
        """Return an error message when the subscription quota is reached."""

        if self.is_quota_exceeded():
            return "You have reached the limit of your plan."

        return None
