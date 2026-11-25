from django.db import models


class CreatedAtModel(models.Model):
    """Base model for entities that require a creation timestamp.

    Order records by creation date in descending order by default.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ("-created_at",)


class DateTimeModel(CreatedAtModel):
    """Extend CreatedAtModel with a timestamp for the last modification.

    Use this base model for entities that need to track both creation
    and subsequent updates.
    """

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta(CreatedAtModel.Meta):
        abstract = True
