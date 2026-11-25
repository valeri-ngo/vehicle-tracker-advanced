from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import AccountRegistrationForm


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


class HomeView(TemplateView):
    """Display the public landing page."""

    template_name = "accounts/home.html"
