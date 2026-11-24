from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.db import IntegrityError, transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import AccountRegistrationForm


class AccountRegisterView(CreateView):
    form_class = AccountRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:account-login")

    def form_valid(self, form):
        """Register a new account and assign the Free subscription group."""

        try:
            with transaction.atomic():
                response = super().form_valid(form)

                free_group = Group.objects.get(name="Free")
                self.object.groups.add(free_group)

        except IntegrityError as error:
            constraint_name = getattr(
                getattr(error.__cause__, "diag", None),
                "constraint_name",
                None,
            )

            if constraint_name != "unique_account_email_case_insensitive":
                raise

            self.object = None
            form.add_error("email", "This email is already in use.")

            return self.form_invalid(form)

        return response


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"
    next_page = "accounts:account-dashboard"


class AccountLogoutView(LogoutView):
    next_page = "accounts:account-login"


class AccountDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"


class HomeView(TemplateView):
    """Display the public landing page."""

    template_name = "accounts/home.html"
