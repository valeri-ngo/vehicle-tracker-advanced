from maintenance.models import Part


class UserPartsQuerysetMixin:
    """Restrict selectable parts to those owned by the current user."""

    def __init__(self, *args, user, **kwargs):
        """Initialize the form with parts belonging to the given user."""

        super().__init__(*args, **kwargs)

        self.fields["parts"].queryset = Part.objects.filter(owner_id=user.pk)
