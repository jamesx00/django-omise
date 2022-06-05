import json

from .mockdata.customer import customer_response


def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, raw_response, status_code):
            self.status_code = status_code
            self.raw_response = raw_response

        def json(self):
            return json.loads(self.raw_response)

    if args[0] == "https://api.omise.co/customers":
        return MockResponse(customer_response, 200)

    return MockResponse(None, 404)


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, raw_response, status_code):
            self.status_code = status_code
            self.raw_response = raw_response

        def json(self):
            return json.loads(self.raw_response)

    request_url = args[0]

    if "https://api.omise.co/customers" in request_url:
        return MockResponse(customer_response, 200)

    return MockResponse(None, 404)
