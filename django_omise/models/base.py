import uuid
from django.apps import apps
from django.db import models

from django_omise.omise import omise
from django_omise.utils import is_omise_object_instances

from typing import Optional


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

    @classmethod
    def update_or_create_from_omise_object(
        cls,
        omise_object: omise.Base,
        uid: Optional[uuid.UUID] = None,
    ) -> "__class__":
        """
        Update existing charge or create a new charge from Omise Charge object.

        :param omise_object: An instance of Omise object
        :param uuid optional: A unique id for new object.

        :returns: An instance of current class
        """
        fields = cls._meta.get_fields()

        defaults = {}

        for field in fields:
            if field.name == "metadata":
                defaults["metadata"] = getattr(
                    omise_object,
                    field.name,
                ).__dict__.get("_attributes")
                continue

            if field.name in cls.NON_DEFAULT_FIELDS:
                continue

            if callable(getattr(omise_object, field.name, None)):
                continue

            if type(field) is models.ForeignKey:
                value = getattr(omise_object, field.name, None)

                if value is None:
                    defaults[f"{field.name}_id"] = value
                elif type(value) is str:
                    defaults[f"{field.name}_id"] = value
                else:
                    if type(value) == omise.Card:
                        card = value
                        Card = apps.get_model(
                            app_label="django_omise", model_name="Card"
                        )
                        Card.update_or_create_from_omise_object(
                            omise_object=card,
                        )

                    elif type(value) == omise.Source:
                        source = value
                        Source = apps.get_model(
                            app_label="django_omise", model_name="Source"
                        )
                        Source.update_or_create_from_omise_object(
                            omise_object=source,
                        )

                    else:
                        raise ValueError("Field not implemented")

                    defaults[f"{field.name}_id"] = getattr(omise_object, field.name).id

                continue

            if is_omise_object_instances(getattr(omise_object, field.name, None)):
                defaults[f"{field.name}_id"] = getattr(omise_object, field.name).id
                continue

            if (
                isinstance(field, (models.TextField, models.CharField))
                and getattr(omise_object, field.name, None) is None
            ):
                defaults[field.name] = ""
                continue

            if (
                getattr(omise_object, field.name, None) is None
                and field.null == False
                and field.default
            ):
                defaults[field.name] = field.default()
                continue

            defaults[field.name] = getattr(omise_object, field.name, None)

        new_object, created = cls.objects.update_or_create(
            pk=omise_object.id,
            livemode=omise_object.livemode,
            defaults=defaults,
        )

        if uid:
            new_object.uid = uid
            new_object.save()

        return new_object
