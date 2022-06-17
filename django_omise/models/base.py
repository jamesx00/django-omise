from __future__ import annotations

import uuid
from django.apps import apps
from django.db import models

from django_omise.omise import omise
from django_omise.utils.core_utils import (
    update_or_create_from_omise_object,
)

from django.utils.translation import gettext_lazy as _

from typing import Optional, Dict
from .managers import DeletableManager

from typing import List


class OmiseMetadata(models.Model):

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Custom metadata for this object."),
    )

    def set_metadata(self, metadata: Optional[Dict] = None) -> "OmiseBaseModel":
        """
        Set the object's medata both on Omise and the Django object.

        :params metadata: A dictionary for medatada

        :returns: Currenct object.
        """

        if metadata is None:
            metadata = {}

        omise_object = self.omise_class.retrieve(self.id)
        omise_object.update(metadata=metadata)

        self.metadata = metadata
        self.save()

        return self

    class Meta:
        abstract = True


class OmiseBaseModel(models.Model):

    id = models.CharField(max_length=255, primary_key=True)
    livemode = models.BooleanField()
    data = models.JSONField(default=dict, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    NON_DEFAULT_FIELDS = [
        "id",
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

    def get_omise_object(self) -> omise.Base:
        """Fetch the object from Omise's server."""
        return self.omise_class.retrieve(self.id)

    def reload_from_omise(
        self, ignore_fields: Optional[List[str]] = None
    ) -> OmiseBaseModel:
        """
        Reload the data from Omise's server and return the saved object

        :param ignore_fields: List of field names to ignore.
        """
        omise_object = self.omise_class.retrieve(self.id)
        return self.__class__.update_or_create_from_omise_object(
            omise_object=omise_object,
            ignore_fields=ignore_fields,
        )

    @classmethod
    def update_or_create_from_omise_object(
        cls,
        omise_object: omise.Base,
        ignore_fields: Optional[List[str]] = None,
        uid: Optional[uuid.UUID] = None,
    ) -> OmiseBaseModel:
        """
        Update existing charge or create a new charge from Omise Charge object.

        :param omise_object: An instance of Omise object
        :param ignore_fields optional: List of field names to ignore
        :param uuid optional: A unique id for new object.

        :returns: An instance of current class
        """
        defaults = cls.build_defaults_from_omise_object(
            omise_object=omise_object,
            ignore_fields=ignore_fields,
            uid=uid,
        )

        new_object, created = cls.objects.update_or_create(
            pk=omise_object.id,
            defaults=defaults,
        )

        return new_object

    @classmethod
    def build_defaults_from_omise_object(
        cls,
        omise_object: omise.Base,
        ignore_fields: Optional[List[str]] = None,
        uid: Optional[uuid.UUID] = None,
    ) -> Dict:
        """
        Create a dictionary of fields and values to use in objects.update_or_create method.

        :param omise_object: Any of the object from omise package. e.g. omise.Charge, omise.Customer, omise.Card
        :param ignore_fields: List of field names as a string to ignore.
        :param uid: The uid of the object. If this is not specify, a new uid will be created for the object.

        :returns: Dictionary of fields and values as keys and values
        """
        fields = cls.get_field_names(
            ignore_fields=ignore_fields,
        )

        fields = [field for field in fields if field.name not in cls.NON_DEFAULT_FIELDS]

        defaults = {}

        if uid is not None:
            defaults["uid"] = uid

        for field in fields:
            if field.name == "metadata":
                defaults["metadata"] = getattr(
                    omise_object,
                    field.name,
                ).__dict__.get("_attributes")
                continue

            if callable(getattr(omise_object, field.name, None)):
                continue

            if (
                getattr(getattr(omise_object, field.name, None), "object", None)
                == "list"
            ):
                values = getattr(omise_object, field.name)
                for value in values:
                    update_or_create_from_omise_object(omise_object=value)
                continue

            if type(field) in [models.ForeignKey, models.OneToOneField]:
                value = getattr(omise_object, field.name, None)

                if value is None or type(value) is str:
                    defaults[f"{field.name}_id"] = value
                else:

                    new_object = update_or_create_from_omise_object(omise_object=value)

                    defaults[field.name] = new_object

                continue

            if (
                type(field) in [models.TextField, models.CharField]
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

        return defaults

    @classmethod
    def get_field_names(
        cls,
        ignore_fields: Optional[List[str]] = None,
    ) -> List[models.fields.Field]:
        """
        Get a list of fields of the class.

        :param ignore_fields: List of field names as a string to ignore.
        :param additional_fields: List of field names as tuple of field name and field type
        """
        ignore_fields = [] if ignore_fields is None else ignore_fields

        fields = [
            field for field in cls._meta.get_fields() if field.name not in ignore_fields
        ]

        return fields


class OmiseDeletableModel(models.Model):
    deleted = models.BooleanField(
        default=False,
        help_text=_("Whether this object is marked as deleted on Omise's server"),
    )

    objects = DeletableManager()

    class Meta:
        abstract = True
