from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView

from notifications.models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """Display notifications belonging to the authenticated user."""

    model = Notification
    template_name = "notifications/notification_list.html"
    context_object_name = "notifications"

    def get_queryset(self) -> QuerySet[Notification]:
        """Return the current user's notifications in reverse chronological order."""

        return (
            super()
            .get_queryset()
            .filter(
                recipient_id=self.request.user.pk,
            )
            .order_by("-created_at")
        )


class NotificationMarkAsReadView(LoginRequiredMixin, View):
    """Mark notifications belonging to the current user as read.

    Restrict state changes to POST requests and avoid unnecessary
    database updates for notifications that have already been read.
    """

    def post(self, request: HttpRequest, pk: int) -> HttpResponseRedirect:
        """Mark the selected notification as read and redirect to the list."""

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
