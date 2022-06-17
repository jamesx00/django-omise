from __future__ import annotations

import omise
import uuid

from django.apps import apps
from django.conf import settings

from typing import Optional, Any, TYPE_CHECKING, List, Dict

if TYPE_CHECKING:
    from django.db import models
    from django_omise.models.base import OmiseBaseModel


def get_payment_methods_for_form(
    payment_methods: Optional[List[str]] = None,
) -> List[str]:
    """
    Get the payment method as per setting for checkout form

    :returns: List of payment methods by setting OMISE_PAYMENT_METHODS or default to credit card only.
    """
    if payment_methods is None:
        payment_methods = get_payment_methods()

    if "card" in payment_methods:
        payment_methods += ["old_card", "new_card"]

    return payment_methods


def get_payment_methods() -> List[str]:
    """
    Get the payment method as per setting

    :returns: List of payment methods by setting OMISE_PAYMENT_METHODS or default to credit card only.
    """
    payment_methods = setting("OMISE_PAYMENT_METHODS", ["card"])
    return payment_methods


def get_payment_methods_by_country(country: Optional[str] = None) -> List[str]:
    """
    Get the payment methods supported by country

    :param country: 3-digit country code.

    :returns: List of supported payment methods
    """
    payment_methods = [
        "card",
    ]

    if country is None:
        country = setting("OMISE_COUNTRY", "THA")

    if country in ["THA", "JPN"]:
        payment_methods.append("internet_banking")

    return payment_methods


def setting(name: str, default: Optional[Any] = None) -> Optional[Any]:
    """
    Helper function to get a Django setting by name. If setting doesn't exists
    it will return a default.

    :param name: Name of setting
    :param default: Value if setting is unfound
    :returns: Setting's value
    """
    return getattr(settings, name, default)


def is_omise_object_instances(value) -> bool:
    """
    Check if a value is an instance of Omise Classes.

    See all the classes here https://github.com/omise/omise-python/blob/master/omise/__init__.py

    :param value: The value to check.

    :returns: True if value is an instance of Omise Classes, False otherwise
    """
    return isinstance(
        value,
        (
            omise.Account,
            omise.Balance,
            omise.BankAccount,
            omise.Capability,
            omise.Card,
            omise.Chain,
            omise.Charge,
            omise.Collection,
            omise.Customer,
            omise.Dispute,
            omise.Document,
            omise.Event,
            omise.Forex,
            omise.Link,
            omise.Occurrence,
            omise.Receipt,
            omise.Recipient,
            omise.Refund,
            omise.Search,
            omise.Schedule,
            omise.Source,
            omise.Token,
            omise.Transaction,
            omise.Transfer,
        ),
    )


def update_or_create_from_omise_object(
    omise_object: omise.Base,
    raise_if_not_implemented: bool = False,
    ignore_fields: Optional[List[str]] = None,
    uid: Optional[uuid.UUID] = None,
    raw_event_data: Optional[Dict] = None,
):
    """
    Update or create a new Django object from Omise object.

    :param omise_object: Any of the Omise object.
    :param raise_if_not_implemented: Whether to raise error if there is no model for Omise object. Default is False.
    :param ignore_fields optional: List of field names to ignore
    :param uuid optional: A unique id for new object.
    :param raw_event_data optional: Raw event data from omise webhook.

    :returns: The corresponding model instance.
    """

    before_update_or_create_from_omise_object_action(
        omise_object=omise_object,
        raw_event_data=raw_event_data,
    )

    saved_object = update_or_create_from_omise_object_action(
        omise_object=omise_object,
        raise_if_not_implemented=raise_if_not_implemented,
        ignore_fields=ignore_fields,
        uid=uid,
    )

    after_update_or_create_from_omise_object_action(
        omise_object=omise_object,
        saved_object=saved_object,
        raw_event_data=raw_event_data,
    )

    return saved_object


def before_update_or_create_from_omise_object_action(
    omise_object: omise.Base,
    raw_event_data: Optional[Dict] = None,
):
    """
    This method is run before the function update_or_create_from_omise_object_action,
    allowing an action before the object is created to to database.
    e.g. Saving schedule object without occurences so that there is no contraint error.

    :param omise_object: An instance of Omise object to perform the action on.
    """
    if raw_event_data is None:
        raw_event_data = {}

    if omise_object.object == "refund":
        refund = omise_object
        charge_id = refund.charge
        omise_charge = omise.Charge.retrieve(charge_id)
        update_or_create_from_omise_object_action(
            omise_object=omise_charge,
            ignore_fields=[
                "refunds",
            ],
        )

    if omise_object.object == "schedule":
        update_or_create_from_omise_object_action(
            omise_object=omise_object,
            ignore_fields=[
                "occurrences",
            ],
        )


def after_update_or_create_from_omise_object_action(
    omise_object: omise.Base,
    saved_object: OmiseBaseModel,
    raw_event_data: Optional[Dict] = None,
):
    """
    This method is run before the function update_or_create_from_omise_object_action,
    allowing an action before the object is created to to database.
    e.g. Reloading the Charge object in the database when a refund is created.

    :param omise_object: An instance of Omise object to perform the action on.
    :param saved_object: An object saved to the database.
    """
    if raw_event_data is None:
        raw_event_data = {}

    if omise_object.object == "charge":

        charge = omise_object
        schedule_id = charge._attributes.get("schedule", None)
        omise_schedule = None
        schedule = None

        if schedule_id:
            omise_schedule = omise.Schedule.retrieve(schedule_id)
            schedule = update_or_create_from_omise_object_action(
                omise_object=omise_schedule
            )

        charge = saved_object
        charge.schedule = schedule
        charge.save()

    if omise_object.object == "customer":

        customer = saved_object

        for schedule in customer.schedules:
            schedule.reload_from_omise()


def update_or_create_from_omise_object_action(
    omise_object: omise.Base,
    raise_if_not_implemented: bool = False,
    ignore_fields: Optional[List[str]] = None,
    uid: Optional[uuid.UUID] = None,
) -> models.Model:
    """
    Update or create a new Django object from Omise object.

    :param omise_object: Any of the Omise object.
    :param raise_if_not_implemented: Whether to raise error if there is no model for Omise object. Default is False.
    :param ignore_fields optional: List of field names to ignore
    :param uuid optional: A unique id for new object.

    :returns: The corresponding model instance.
    """
    model = get_model_from_omise_object(
        omise_object=omise_object, raise_if_not_implemented=raise_if_not_implemented
    )

    if model is None:
        return None

    new_object = model.update_or_create_from_omise_object(
        omise_object=omise_object, ignore_fields=ignore_fields, uid=uid
    )
    return new_object


def get_model_from_omise_object(
    omise_object: omise.Base,
    raise_if_not_implemented: bool = False,
) -> OmiseBaseModel:
    """
    Get the model of the django_omise app with a given Omise object.

    :param omise_object: Any of the Omise object.
    :param raise_if_not_implemented: Whether to raise error if there is no model for Omise object. Default is False.

    :returns: The corresponding model class.
    """
    model_map = {
        "card": get_current_app_model(model_name="Card"),
        "customer": get_current_app_model(model_name="Customer"),
        "charge": get_current_app_model(model_name="Charge"),
        "source": get_current_app_model(model_name="Source"),
        "event": get_current_app_model(model_name="Event"),
        "refund": get_current_app_model(model_name="Refund"),
        "scheduled_charge": get_current_app_model(model_name="ChargeSchedule"),
        "occurrence": get_current_app_model(model_name="Occurrence"),
        "schedule": get_current_app_model(model_name="Schedule"),
    }

    if (
        raise_if_not_implemented
        and getattr(omise_object, "object", None) not in model_map
    ):
        raise ValueError(
            f"The object {getattr(omise_object, 'object', None) } has not been implemented"
        )

    return model_map.get(getattr(omise_object, "object", None), None)


def get_current_app_model(model_name: str) -> models.Model:
    """
    Get the model of the django_omise app with a given model name.

    :param model_name str: The model name.

    :returns: The corresponding model class.
    """
    app_label = "django_omise"
    return apps.get_model(app_label=app_label, model_name=model_name)
