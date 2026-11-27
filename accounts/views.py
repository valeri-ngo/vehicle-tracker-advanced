from datetime import timedelta
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.db import IntegrityError, transaction
from django.db.models import F, Q, QuerySet
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, TemplateView

from common.quotas import SUBSCRIPTION_LIMITS, get_subscription_plan
from documents.models import VehicleDocument
from maintenance.models import MaintenanceItem, MaintenanceSchedule, ServiceRecord
from notifications.models import Notification
from vehicles.models import OdometerEntry

from .forms import AccountRegistrationForm
from .models import Account


class AccountRegisterView(CreateView):
    """Handle account registration and assign the default subscription plan.

    Create the account and its Free group membership within a single
    transaction to prevent partially registered accounts. Handle duplicate
    email addresses reported by the database during registration.
    """

    form_class = AccountRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:account-login")

    def _assign_free_group(self) -> None:
        """Assign the newly registered account to the default Free subscription group."""

        free_group = Group.objects.get(name="Free")
        self.object.groups.add(free_group)

    @staticmethod
    def _is_duplicate_email_error(error: IntegrityError) -> bool:
        """Check whether the database error was caused by a duplicate email address."""

        constraint_name = getattr(
            getattr(error.__cause__, "diag", None),
            "constraint_name",
            None,
        )

        return constraint_name == "unique_account_email_case_insensitive"

    def form_valid(self, form: AccountRegistrationForm) -> HttpResponse:
        """Register a new account and assign the Free subscription group."""

        try:
            with transaction.atomic():
                response = super().form_valid(form)

                self._assign_free_group()

        except IntegrityError as error:
            if not self._is_duplicate_email_error(error):
                raise

            self.object = None
            form.add_error("email", "This email is already in use.")

            return self.form_invalid(form)

        return response


class AccountLoginView(LoginView):
    """Authenticate users and redirect them to the account dashboard by default."""

    template_name = "accounts/login.html"
    next_page = "accounts:account-dashboard"


class AccountLogoutView(LogoutView):
    """End the current user session and redirect to the login page."""

    next_page = "accounts:account-login"


class AccountDashboardView(LoginRequiredMixin, TemplateView):
    """Display the dashboard for authenticated users.

    Provide the main entry point for managing vehicles, maintenance
    records, documents and account-related information.
    """

    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Provide dashboard data for the authenticated user."""
        context = super().get_context_data(**kwargs)

        user = self.request.user

        statistics = self._get_statistics(user)
        upcoming_maintenance = self._get_upcoming_maintenance(user)
        expiring_documents = self._get_expiring_documents(user)
        recent_service_records = self._get_recent_service_records(user)
        recent_notifications = self._get_recent_notifications(user)
        subscription_context = self._get_subscription_context(user, statistics)

        context["upcoming_maintenance"] = upcoming_maintenance
        context["expiring_documents"] = expiring_documents
        context["recent_service_records"] = recent_service_records
        context["recent_notifications"] = recent_notifications

        context.update(statistics)
        context.update(subscription_context)

        return context

    @staticmethod
    def _get_statistics(user: Account) -> dict[str, int]:
        """Retrieve the statistics for a particular user."""

        vehicle_count = user.vehicles.count()

        service_record_count = ServiceRecord.objects.filter(vehicle__owner=user).count()

        active_schedule_count = MaintenanceSchedule.objects.filter(
            vehicle__owner=user,
            is_completed=False,
        ).count()

        document_count = VehicleDocument.objects.filter(vehicle__owner=user).count()

        maintenance_item_count = MaintenanceItem.objects.filter(owner=user).count()

        unread_notification_count = Notification.objects.filter(
            recipient=user,
            is_read=False,
        ).count()

        odometer_entry_count = OdometerEntry.objects.filter(vehicle__owner=user).count()

        return {
            "vehicle_count": vehicle_count,
            "service_record_count": service_record_count,
            "active_schedule_count": active_schedule_count,
            "document_count": document_count,
            "maintenance_item_count": maintenance_item_count,
            "unread_notification_count": unread_notification_count,
            "odometer_entry_count": odometer_entry_count,
        }

    @staticmethod
    def _get_upcoming_maintenance(user: Account) -> QuerySet[MaintenanceSchedule]:
        """Return upcoming and overdue maintenance schedules for a user."""

        upcoming_maintenance = MaintenanceSchedule.objects.filter(
            vehicle__owner=user,
            is_completed=False,
        )

        today = timezone.localdate()
        date_threshold = today + timedelta(days=30)

        mileage_threshold = F("vehicle__current_mileage") + 3000

        upcoming_maintenance = (
            upcoming_maintenance.filter(
                Q(due_date__lte=date_threshold) | Q(due_mileage__lte=mileage_threshold)
            )
            .order_by(
                F("due_date").asc(nulls_last=True),
                F("due_mileage").asc(nulls_last=True),
            )
            .select_related("vehicle")
        )[:5]

        return upcoming_maintenance

    @staticmethod
    def _get_expiring_documents(user: Account) -> QuerySet[VehicleDocument]:
        """Return up to five expired or soon-to-expire documents for a user."""

        today = timezone.localdate()
        date_threshold = today + timedelta(days=30)

        return (
            VehicleDocument.objects.filter(
                vehicle__owner=user,
                expires_on__lte=date_threshold,
            )
            .order_by("expires_on")
            .select_related("vehicle")[:5]
        )

    @staticmethod
    def _get_recent_service_records(user: Account) -> QuerySet[ServiceRecord]:
        """Return the five most recent service records for a user."""

        return (
            ServiceRecord.objects.filter(
                vehicle__owner=user,
            )
            .order_by("-service_date", "-pk")
            .select_related("vehicle")[:5]
        )

    @staticmethod
    def _get_recent_notifications(user: Account) -> QuerySet[Notification]:
        """Return the five most recent notifications for a user."""

        return Notification.objects.filter(
            recipient=user,
        ).order_by(
            "-created_at",
            "-pk",
        )[:5]

    @staticmethod
    def _get_subscription_context(
        user: Account, statistics: dict[str, int]
    ) -> dict[str, Any]:
        """Provide subscription details and resource usage for a user."""

        plan = get_subscription_plan(user)

        if plan == "Superuser":
            limits = dict.fromkeys(SUBSCRIPTION_LIMITS["Free"].keys(), None)

        else:
            limits = SUBSCRIPTION_LIMITS[plan]

        resource_usage = {
            "vehicles": statistics["vehicle_count"],
            "service_records": statistics["service_record_count"],
            "odometer_entries": statistics["odometer_entry_count"],
            "maintenance_schedules": statistics["active_schedule_count"],
            "maintenance_items": statistics["maintenance_item_count"],
            "documents": statistics["document_count"],
        }

        usage = {}

        for resource, used in resource_usage.items():
            limit = limits[resource]
            is_unlimited = limit is None

            if limit is None:
                remaining = None
                percentage = None

            else:
                remaining = max(0, limit - used)
                percentage = round((used / limit) * 100, 2)

            usage[resource] = {
                "used": used,
                "limit": limit,
                "remaining": remaining,
                "percentage": percentage,
                "is_unlimited": is_unlimited,
            }

        return {"subscription_plan": plan, "subscription_usage": usage}


class HomeView(TemplateView):
    """Display the public landing page."""

    template_name = "accounts/home.html"
