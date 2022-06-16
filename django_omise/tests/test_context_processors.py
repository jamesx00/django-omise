from django.test import TestCase
from django_omise.context_processors import omise_keys
from django.conf import settings

from django_omise.tests.mock_django import MockRequest

# Create your tests here.
class ContextProcessorTestCase(TestCase):
    def test_omise_public_key(self):
        self.assertEqual(
            omise_keys(request=MockRequest())["omise_public_key"],
            settings.OMISE_PUBLIC_KEY,
        )
