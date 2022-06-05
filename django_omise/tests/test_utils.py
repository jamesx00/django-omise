import json

from .mockdata.customer import customer_response, add_card_response
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
