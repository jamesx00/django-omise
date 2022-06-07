from django.test import TestCase

from django_omise.models.core import Source
from django_omise.models.choices import Currency

# Create your tests here.
class SourceTestCase(TestCase):
    def test_source_human_amount(self):
        source = Source(amount=100000, currency=Currency.THB)
        self.assertEqual(source.human_amount, "1,000.00")

    def test_source_human_amount_jpy(self):
        source = Source(amount=100000, currency=Currency.JPY)
        self.assertEqual(source.human_amount, "100,000.00")

    def test_source_type_name_not_exists(self):
        source = Source(amount=100000, currency=Currency.JPY, type="not_real_source")
        with self.assertRaises(KeyError):
            source.source_type_name
