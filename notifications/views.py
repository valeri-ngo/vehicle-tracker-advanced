from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView

from notifications.models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """Display notifications belonging to the authenticated user."""

    model = Notification
    template_engine = "notifications/notification_list.html"
    context_object_name = "notifications"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                recipient_id=self.request.user.pk,
            )
            .order_by("-created_at")
        )


class NotificationMarkAsReadView(LoginRequiredMixin, View):
    """Mark an owned notification as read."""

    def post(self, request, pk):
        notification = get_object_or_404(
            Notification,
            pk=pk,
            recipient_id=request.user.pk,
        )

        if not notification.is_read:
            notification.is_read = True
            notification.save(
                update_fields=["is_read", "updated_at"],
            )

        return redirect("notifications:notification-list")
