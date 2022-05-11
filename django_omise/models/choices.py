from django.db import models
from django.utils.translation import gettext_lazy as _

class ChargeStatus(models.TextChoices):
    FAILED = "failed", _("Failed")
    EXPIRED = "expired", _("Expired")
    PENDING = "pending", _("Pending")
    REVERSED = "reverse", _("Reversed")
    SUCCESSFUL = "successful", _("Successful")
    UNKNOWN = "unknown", _("Unknown")

class Currency(models.TextChoices):
    USD = (
        "USD",
        _("United States Dollar"),
    )
    THB = (
        "THB",
        _("Thai Baht"),
    )
    SGD = (
        "SGD",
        _("Singapore Dollar"),
    )
    JPY = (
        "JPY",
        _("Japanese Yen"),
    )
    GBP = (
        "GBP",
        _("Pound Sterling"),
    )
    EUR = (
        "EUR",
        _("Euro"),
    )
    CNY = (
        "CNY",
        _("Chinese Yuan"),
    )
    AUD = (
        "AUD",
        _("Australian Dollar"),
    )
