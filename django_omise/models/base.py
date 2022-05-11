import uuid
from django.db import models


class OmiseBaseModel(models.Model):

    id = models.CharField(max_length=255, primary_key=True)
    livemode = models.BooleanField()
    data = models.JSONField(default=dict, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    NON_DEFAULT_FIELDS = [
        "id",
        "livemode",
        "date_created",
        "date_updated",
        "data",
        "uid",
    ]

    def __str__(self):
        return f"Omise{self.__class__.__name__}: {self.id}"

    class Meta:
        abstract = True
        ordering = [
            "-date_created",
        ]
