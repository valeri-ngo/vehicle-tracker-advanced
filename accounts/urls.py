from django.urls import path

from .views import (
    AccountDashboardView,
    AccountLoginView,
    AccountLogoutView,
    AccountRegisterView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", view=AccountRegisterView.as_view(), name="account-register"),
    path("login/", view=AccountLoginView.as_view(), name="account-login"),
    path("logout/", view=AccountLogoutView.as_view(), name="account-logout"),
    path("dashboard/", view=AccountDashboardView.as_view(), name="account-dashboard"),
]
