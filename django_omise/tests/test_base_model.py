from django.test import TestCase

from django_omise.models.core import Customer

from django_omise.tests.mockdata.charge import (
    base_charge_response,
    base_charge_with_metadata_response,
)

from django_omise.tests.test_utils import (
    mocked_base_charge_request,
    mocked_set_charge_metadata_request,
)

from django_omise.tests.base import OmiseBaseTestCase

from unittest import mock

# Create your tests here.
class BaseModelTestCase(OmiseBaseTestCase):
    def test_class_get_field_names(self):
        field_names = [field.name for field in Customer.get_field_names()]
        fields = Customer._meta.get_fields()
        for field in fields:
            self.assertIn(field.name, field_names)

    def test_class_get_field_name_with_ignored_fields(self):
        test_field = Customer._meta.get_fields()[0]
        field_names = [
            field.name
            for field in Customer.get_field_names(ignore_fields=[test_field.name])
        ]
        self.assertNotIn(test_field.name, field_names)

    @mock.patch("requests.patch", side_effect=mocked_set_charge_metadata_request)
    @mock.patch("requests.get", side_effect=mocked_base_charge_request)
    def test_set_metadata_with_none(self, mock_get_charge, mock_set_metadata):
        metadata = None
        django_charge = self.create_charge()
        django_charge.set_metadata(metadata=metadata)

        mock_set_metadata.assert_called_once()

        self.assertEqual(django_charge.metadata, dict())

    @mock.patch("requests.patch", side_effect=mocked_set_charge_metadata_request)
    @mock.patch("requests.get", side_effect=mocked_base_charge_request)
    def test_set_metadata_with_data(self, mock_get_charge, mock_set_metadata):
        metadata = {"data": "data"}
        django_charge = self.create_charge()
        django_charge.set_metadata(metadata=metadata)

        mock_set_metadata.assert_called_once()

        self.assertEqual(django_charge.metadata, metadata)

    @mock.patch("omise.Charge.retrieve")
    def test_get_omise_object(self, mock_omise_retrieve):
        charge = self.create_charge()
        charge.get_omise_object()
        mock_omise_retrieve.assert_called_once_with(charge.id)

    @mock.patch(
        "django_omise.models.base.OmiseBaseModel.update_or_create_from_omise_object"
    )
    @mock.patch("requests.get", side_effect=mocked_base_charge_request)
    def test_reload_from_omise(self, mock_get_charge, mock_update_or_create_method):
        charge = self.create_charge()
        customer = self.create_customer(id="cust_test_5s1jz157366mu6wr0ng")
        charge.reload_from_omise()
        mock_update_or_create_method.assert_called_once()

    def test_str_method(self):
        charge = self.create_charge()
        self.assertIsInstance(str(charge), str)
