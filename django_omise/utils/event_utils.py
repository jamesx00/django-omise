from django_omise.models.event import EventType, Event
from django_omise.models.core import Charge
from django_omise.omise import omise


def pre_event_handle(omise_event: omise.Event):
    """
    Perform additional actions on Omise Event object before handling with the webhook view.

    :params omise_event: The Omise Event object

    :returns: None
    """
    if omise_event.key == EventType.REFUND_CREATE.value:
        charge = Charge.objects.get(pk=omise_event.data.charge)
        charge.reload_from_omise()


def post_event_handle(omise_event: omise.Event, event_object: Event):
    """
    Perform additional actions on Omise Event object after handling with the webhook view.

    :params omise_event: The Omise Event object
    :param event_object: The new event object in the database

    :returns: None
    """
