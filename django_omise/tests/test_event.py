from django_omise.models.schedule import Schedule
from django_omise.omise import omise
from django_omise.utils.core_utils import update_or_create_from_omise_object

from django_omise.tests.base import OmiseBaseTestCase

from unittest import mock

from .test_utils import mocked_schedule_event_request

# Create your tests here.
class EventTestCase(OmiseBaseTestCase):
    def setUp(self):
        self.customer = self.create_customer(id="test_customer_id")
        self.card = self.create_card(id="test_card_id")

    @mock.patch("requests.get", side_effect=mocked_schedule_event_request)
    def test_schedule_event(self, mock_schedule_event):
        event = omise.Event.retrieve("test_event_id")
        event_data = event.data
        schedule = update_or_create_from_omise_object(omise_object=event_data)
        self.assertTrue(Schedule.objects.filter(id=schedule.id).exists())
