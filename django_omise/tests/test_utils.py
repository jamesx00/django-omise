import json

from .mockdata.card import delete_card_response
from .mockdata.charge import (
    base_charge_response,
    base_charge_with_metadata_response,
    base_charge_jpy,
    partially_refunded_response,
    fully_refunded_response,
)
from .mockdata.customer import customer_response, add_card_response
from .mockdata.event import schedule_with_one_charge_event_response
from .mockdata.schedule import base_schedule_response
from .mockdata.token import token_response


class MockResponse:
    def __init__(self, raw_response, status_code):
        self.status_code = status_code
        self.raw_response = raw_response

    def json(self):
        return json.loads(self.raw_response)


def mocked_requests_post(*args, **kwargs):

    request_url = args[0]

    if request_url == "https://api.omise.co/customers":  # omise.Customer.create
        return MockResponse(customer_response, 200)

    if request_url == "https://vault.omise.co/tokens":  # omise.Token.create
        return MockResponse(customer_response, 200)

    return MockResponse(None, 404)


def mocked_requests_get(*args, **kwargs):

    request_url = args[0]

    if "https://api.omise.co/customers" in request_url:  # omise.Customer.retrieve
        return MockResponse(customer_response, 200)

    if (
        request_url == "https://vault.omise.co/tokens/test_token_id"
    ):  # omise.Token.retrieve
        return MockResponse(token_response, 200)

    return MockResponse(None, 404)


def mocked_base_charge_request(*args, **kwargs):
    return MockResponse(base_charge_response, 200)


def mocked_set_charge_metadata_request(*args, **kwargs):
    return MockResponse(base_charge_with_metadata_response, 200)


def mocked_charge_with_card_request(*args, **kwargs):
    return MockResponse(base_charge_response, 200)


def mocked_partially_refunded_charge_request(*args, **kwargs):
    return MockResponse(partially_refunded_response, 200)


def mocked_fully_refunded_charge_request(*args, **kwargs):
    return MockResponse(fully_refunded_response, 200)


def mocked_jpy_charge(*args, **kwargs):
    return MockResponse(base_charge_jpy, 200)


def mocked_add_card_request(*args, **kwargs):
    return MockResponse(add_card_response, 200)


def mocked_delete_card_request(*args, **kwargs):
    return MockResponse(delete_card_response, 200)


def mocked_base_schedule_request(*args, **kwargs):
    return MockResponse(base_schedule_response, 200)


def mocked_schedule_event_request(*args, **kwargs):
    return MockResponse(schedule_with_one_charge_event_response, 200)
