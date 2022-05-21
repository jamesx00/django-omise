from django_omise.models.event import EventType
from django_omise.models.core import Charge
from django_omise.omise import omise


def handle_event(event: omise.Event):
    """
    Perform additional actions on Omise Event object

    :returns: None
    """
    if event.key == EventType.REFUND_CREATE.value:
        charge = Charge.objects.get(pk=event.data.charge)
        charge.reload_from_omise()
