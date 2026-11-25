from django.urls import path

from .views import (
    AccountDashboardView,
    AccountLoginView,
    AccountLogoutView,
    AccountRegisterView,
    HomeView,
)

app_name = "accounts"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("register/", AccountRegisterView.as_view(), name="account-register"),
    path("login/", AccountLoginView.as_view(), name="account-login"),
    path("logout/", AccountLogoutView.as_view(), name="account-logout"),
    path("dashboard/", AccountDashboardView.as_view(), name="account-dashboard"),
]
