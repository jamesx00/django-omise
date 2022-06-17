from django_omise.models.event import EventType, Event
from django_omise.models.core import Charge
from django_omise.omise import omise

from django_omise.utils.core_utils import update_or_create_from_omise_object


from typing import Dict


def pre_event_handle(omise_event: omise.Event, raw_event: Dict):
    """
    Perform additional actions on Omise Event object before handling with the webhook view.

    :params omise_event: The Omise Event object
    :param raw_event: The event data as received with webhook view

    :returns: None
    """
    pass


def post_event_handle(omise_event: omise.Event, event_object: Event, raw_event: Dict):
    """
    Perform additional actions on Omise Event object after handling with the webhook view.

    :params omise_event: The Omise Event object
    :param event_object: The new event object in the database
    :param raw_event: The event data as received with webhook view

    :returns: None
    """
    pass
