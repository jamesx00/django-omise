import json

from django.contrib import admin
from django.utils.html import format_html

# Register your models here.
from .models.core import Customer, Card, Charge, Source
from .models.event import Event


class CardInline(admin.TabularInline):

    model = Card

    fields = (
        "id",
        "last_digits",
        "deleted",
    )

    extra = 0

    def has_change_permission(self, request, obj=None):
        return False


class ChargeInline(admin.StackedInline):

    model = Charge
    extra = 0
    can_delete = False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    search_fields = (
        "user__email",
        "user__username",
        "id",
    )

    list_display = (
        "id",
        "deleted",
        "user",
        "livemode",
        "date_created",
        "date_updated",
    )

    readonly_fields = ("uid",)

    inlines = [
        CardInline,
        ChargeInline,
    ]

    list_filter = (
        "livemode",
        "date_created",
        "date_updated",
        "deleted",
    )


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "id",
        "livemode",
        "last_digits",
        "deleted",
        "date_created",
        "date_updated",
    )
    list_filter = (
        "livemode",
        "deleted",
        "date_created",
        "date_updated",
    )

    readonly_fields = ("uid",)
    search_fields = ("customer__user__email", "customer__user__username", "id")

    inlines = [
        ChargeInline,
    ]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "livemode",
        "event_type",
        "date_created",
    )
    readonly_fields = (
        "uid",
        "event_object",
        "content_type",
        "object_id",
    )
    list_filter = ("livemode", "date_created", "date_updated", "event_type")

    fields = (
        "id",
        "livemode",
        "event_type",
        "event_data",
        "uid",
        "event_object",
        "content_type",
        "object_id",
    )

    def event_data(self, obj=None):
        return format_html("<pre>{}</pre>", json.dumps(obj.data, indent=4))

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    search_fields = ("id",)

    def has_change_permission(self, request, obj=None):
        return False

    list_display = (
        "id",
        "livemode",
        "status",
        "date_created",
        "date_updated",
        "amount",
        # "authorize_uri",
        "authorized",
        "capturable",
        "capture",
        # "card",
        "currency",
        # "customer",
        "description",
        "disputable",
        "expired",
        "expired_at",
        "expires_at",
        "failure_code",
        "failure_message",
        "fee",
        "fee_vat",
        "funding_amount",
        "funding_currency",
        "interest",
        "interest_vat",
        "ip",
        "net",
        "paid",
        "paid_at",
        "refundable",
        "refunded_amount",
        "reversed",
        # "source",
        "voided",
        "zero_interest_installments",
    )
    list_filter = (
        "livemode",
        "date_created",
        "date_updated",
        "authorized",
        "capturable",
        "capture",
        "disputable",
        "expired",
        "expired_at",
        "expires_at",
        "paid",
        "paid_at",
        "refundable",
        "reversed",
        "voided",
        "zero_interest_installments",
    )

    readonly_fields = ("uid",)


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "amount",
        "bank",
        "barcode",
        "charge_status",
        "currency",
        "email",
        "flow",
        "installment_term",
        "mobile_number",
        "name",
        "phone_number",
        "platform_type",
        "receipt_amount",
        "store_id",
        "store_name",
        "terminal_id",
        "type",
        "zero_interest_installments",
    )
    list_filter = ("zero_interest_installments",)
    search_fields = (
        "id",
        "name",
    )
    readonly_fields = ("uid",)

    def has_change_permission(self, request, obj=None):
        return False
