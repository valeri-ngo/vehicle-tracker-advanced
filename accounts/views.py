from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import AccountRegistrationForm


class AccountRegisterView(CreateView):
    form_class = AccountRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:account-login")


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"
    next_page = "accounts:account-dashboard"


class AccountLogoutView(LogoutView):
    next_page = "accounts:account-login"


class AccountDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"
