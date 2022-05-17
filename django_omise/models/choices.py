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


class ChargeSourceType(models.TextChoices):
    TRUEMONEY_WALLET = "truemoney", _("TrueMoney Wallet")
    INTERNET_BANKING_BAY = "internet_banking_bay", _("Krungsri Bank")
    INTERNET_BANKING_BBL = "internet_banking_bbl", _("Bangkok Bank")
    INTERNET_BANKING_KTB = "internet_banking_ktb", _("Krungthai Bank")
    INTERNET_BANKING_SCB = "internet_banking_scb", _("SCB Bank")
    PROMPTPAY = "promptpay", _("Promptpay")


class SourceFlow(models.TextChoices):
    REDIRECT = "redirect", _("Redirect")
    OFFLINE = "offline", _("Offline")
    APP_REDIRECT = "app_redirect", _("App Redirect")
