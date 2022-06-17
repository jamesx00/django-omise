import json

from django.urls import reverse
from django_omise.tests.base import ClientAndUserBaseTestCase, OmiseBaseTestCase

from django_omise.tests.mockdata.event import schedule_with_one_charge_event_response
from django_omise.tests.test_utils import mocked_requests_event_schedule

from django_omise.omise import omise


from unittest import mock


class ViewTestCase(ClientAndUserBaseTestCase, OmiseBaseTestCase):
    def setUp(self):
        self.customer = self.create_customer(id="test_customer_id")
        self.card = self.create_card(id="test_card_id")

    def test_webhook_no_json_format_status_code(self):
        response = self.client.post(
            reverse("django_omise:webhook"),
            "This is justa raw body",
            content_type="text/plain",
        )
        self.assertEqual(response.status_code, 400)

    @mock.patch(
        "omise.Event.retrieve",
        side_effect=omise.errors.NotFoundError("event not found"),
    )
    def test_webhook_no_event_found(self, mock_event_retrieve):
        response = self.client.post(
            reverse("django_omise:webhook"),
            schedule_with_one_charge_event_response,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    @mock.patch("requests.get", side_effect=mocked_requests_event_schedule)
    def test_webhook_schedule(self, mock_get_event):
        response = self.client.post(
            reverse("django_omise:webhook"),
            schedule_with_one_charge_event_response,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
