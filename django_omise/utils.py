import omise
from django.conf import settings

from typing import Optional, Any


def setting(name: str, default: Optional[Any] = None) -> Optional[Any]:
    """
    Helper function to get a Django setting by name. If setting doesn't exists
    it will return a default.

    :param name: Name of setting
    :param default: Value if setting is unfound
    :returns: Setting's value
    """
    return getattr(settings, name, default)


def is_omise_object_instances(value) -> bool:
    """
    Check if a value is an instance of Omise Classes.

    See all the classes here https://github.com/omise/omise-python/blob/master/omise/__init__.py

    :param value: The value to check.

    :returns: True if value is an instance of Omise Classes, False otherwise
    """
    return isinstance(
        value,
        (
            omise.Account,
            omise.Balance,
            omise.BankAccount,
            omise.Capability,
            omise.Card,
            omise.Chain,
            omise.Charge,
            omise.Collection,
            omise.Customer,
            omise.Dispute,
            omise.Document,
            omise.Event,
            omise.Forex,
            omise.Link,
            omise.Occurrence,
            omise.Receipt,
            omise.Recipient,
            omise.Refund,
            omise.Search,
            omise.Schedule,
            omise.Source,
            omise.Token,
            omise.Transaction,
            omise.Transfer,
        ),
    )
