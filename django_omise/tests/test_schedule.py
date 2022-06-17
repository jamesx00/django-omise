from django.test import TestCase

import code
import readline

from django_omise.models.schedule import Schedule, Occurrence
from django_omise.omise import omise
from django_omise.utils.core_utils import update_or_create_from_omise_object

from django_omise.tests.base import OmiseBaseTestCase

from unittest import mock

from .test_utils import mocked_base_schedule_request

# Create your tests here.
class CustomerTestCase(OmiseBaseTestCase):
    def setUp(self):
        self.customer = self.create_customer(id="test_customer_id")
        self.card = self.create_card(id="test_card_id")

    @mock.patch("requests.get", side_effect=mocked_base_schedule_request)
    def test_schedule_update_or_create(self, mock_get_schedule):
        omise_schedule = omise.Schedule.retrieve("test_schedule_id")
        schedule = update_or_create_from_omise_object(omise_object=omise_schedule)
        self.assertEqual(Schedule.objects.count(), 1)

    @mock.patch("requests.get", side_effect=mocked_base_schedule_request)
    def test_schedule_occurrence(self, mock_get_schedule):
        omise_schedule = omise.Schedule.retrieve("test_schedule_id")
        schedule = update_or_create_from_omise_object(omise_object=omise_schedule)
        self.assertEqual(
            schedule.occurrences.all().count(), len(omise_schedule.occurrences)
        )
