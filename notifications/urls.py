from django.urls import path

from notifications.views import (
    NotificationListView,
    NotificationMarkAsReadView,
)

app_name = "notifications"

urlpatterns = [
    path(
        "",
        NotificationListView.as_view(),
        name="notification-list",
    ),
    path(
        "<int:pk>/read/",
        NotificationMarkAsReadView.as_view(),
        name="notification-mark-as-read",
    ),
]
