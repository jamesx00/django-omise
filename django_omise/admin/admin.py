import json

from django.contrib import admin
from django.utils.html import format_html

# Register your models here.
from django_omise.models.core import Customer, Card, Charge, Source, Refund
from django_omise.models.choices import ChargeStatus, ScheduleStatus
from django_omise.models.schedule import Schedule, Occurrence, ChargeSchedule
from django_omise.models.event import Event


class CardInline(admin.TabularInline):

    model = Card

    fields = (
        "id",
        "livemode",
        "default_card",
        "deleted",
        "last_digits",
    )

    readonly_fields = [
        "default_card",
    ]

    extra = 0

    show_change_link = True

    can_delete = False

    def has_change_permission(self, request, obj=None):
        return False

    def default_card(self, obj=None):
        if obj and obj.customer:
            return obj.customer.default_card == obj

    default_card.boolean = True


class ChargeScheduleInline(admin.TabularInline):

    model = ChargeSchedule

    fields = [
        # "id",
        "schedule",
        "livemode",
        "human_amount",
        "currency",
        "card",
        "card_available",
        "default_card",
        "colorized_status",
        "next_occurrence_on",
        "schedule_in_words",
        "schedule_period",
    ]

    readonly_fields = [
        "human_amount",
        "schedule",
        "colorized_status",
        "next_occurrence_on",
        "schedule_in_words",
        "schedule_period",
        "card_available",
    ]

    extra = 0
    can_delete = False
    show_change_link = True

    def has_change_permission(self, request, obj=None):
        return False

    def schedule(self, obj=None):
        if obj:
            return obj.schedule

    def schedule_status(self, obj=None):
        if obj:
            return obj.schedule.status

    def next_occurrence_on(self, obj=None):
        if obj and obj.schedule.next_occurrences_on:
            return obj.schedule.next_occurrences_on[0]

    def schedule_in_words(self, obj=None):
        if obj:
            return obj.schedule.in_words

    def schedule_period(self, obj=None):
        if obj:
            return f"{obj.schedule.start_on} - {obj.schedule.end_on}"

    def card_available(self, obj=None):
        if obj and obj.card:
            return not obj.card.deleted

    def colorized_status(self, obj=None):
        if obj:
            if obj.schedule.status == ScheduleStatus.RUNNING:
                return format_html(
                    "<div style='display:inline-block; background-color: green; color: white; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                    obj.schedule.status,
                )

            if obj.schedule.status == ScheduleStatus.EXPIRING:
                return format_html(
                    "<div style='display:inline-block; background-color: yellow; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                    obj.schedule.status,
                )

            if obj.schedule.status == ScheduleStatus.EXPIRED:
                return format_html(
                    "<div style='display:inline-block; background-color: gray; color: white; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                    obj.schedule.status,
                )

            if obj.schedule.status in [
                ScheduleStatus.DELETED,
                ScheduleStatus.SUSPENDED,
            ]:
                return format_html(
                    "<div style='display:inline-block; background-color: gray; color: white; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                    obj.schedule.status,
                )

            return format_html(
                "<div style='display:inline-block; background-color: gray; color: white; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                obj.schedule.status,
            )

    colorized_status.short_description = "Schedule status"

    card_available.boolean = True


class ChargeInline(admin.TabularInline):

    model = Charge
    extra = 0
    can_delete = False

    show_change_link = True

    fields = [
        "id",
        "livemode",
        "colorized_status",
        "human_amount",
        "currency",
        "refunded_amount",
        "refundable",
        "capturable",
        "schedule",
        "card",
        "source",
    ]

    readonly_fields = ("human_amount", "colorized_status")

    def colorized_status(self, obj=None):
        if obj:
            if obj.extended_status == ChargeStatus.SUCCESSFUL:
                return format_html(
                    "<div style='display:inline-block; background-color: green; color: white; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                    obj.extended_status,
                )

            if obj.extended_status == ChargeStatus.FAILED:
                return format_html(
                    "<div style='display:inline-block; background-color: red; color: white; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                    obj.extended_status,
                )

            if obj.extended_status == ChargeStatus.PENDING:
                return format_html(
                    "<div style='display:inline-block; background-color: yellow; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                    obj.extended_status,
                )

            return format_html(
                "<div style='display:inline-block; background-color: gray; color: white; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                obj.extended_status,
            )

    colorized_status.short_description = "status"

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
        ChargeScheduleInline,
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

    readonly_fields = (
        "uid",
        "id",
        "livemode",
        "customer",
        "financing",
        "fingerprint",
    )
    search_fields = ("customer__user__email", "customer__user__username", "id")

    inlines = [
        ChargeScheduleInline,
        ChargeInline,
    ]


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "livemode",
        "date_created",
        "charge",
        "amount",
        "currency",
        "funding_amount",
        "funding_currency",
        "voided",
    )
    list_filter = (
        "livemode",
        "date_created",
        "date_updated",
        "voided",
    )
    search_fields = [
        "charge__id",
    ]

    def has_change_permission(self, request, obj=None):
        return False


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
        "event_object",
        "event_type",
        "event_data",
        "uid",
        "content_type",
        "object_id",
    )

    def event_data(self, obj=None):
        return format_html("<pre>{}</pre>", json.dumps(obj.data, indent=4))

    def has_change_permission(self, request, obj=None):
        return False


class RefundInline(admin.TabularInline):
    model = Refund

    extra = 0

    fields = ["id", "livemode", "human_amount", "currency", "voided"]
    readonly_fields = ("human_amount",)

    def has_change_permission(self, request, obj=None):
        return False

    show_change_link = True


@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    search_fields = (
        "id",
        "customer__user__email",
        "customer__user__username",
    )

    def has_change_permission(self, request, obj=None):
        return False

    list_display = (
        "id",
        "livemode",
        "date_created",
        "date_updated",
        "colorized_status",
        "human_amount",
        "currency",
        "refunded_amount",
        "refundable",
        "source_type",
        "schedule",
        "description",
        "failure_message",
        "source",
        "voided",
        "zero_interest_installments",
    )
    list_filter = (
        "status",
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

    inlines = [
        RefundInline,
    ]

    readonly_fields = ("uid", "source_type", "colorized_status")

    def colorized_status(self, obj=None):
        if obj:
            if obj.extended_status == ChargeStatus.SUCCESSFUL:
                return format_html(
                    "<div style='display:inline-block; background-color: green; color: white; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                    obj.extended_status,
                )

            if obj.extended_status == ChargeStatus.FAILED:
                return format_html(
                    "<div style='display:inline-block; background-color: red; color: white; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                    obj.extended_status,
                )

            if obj.extended_status == ChargeStatus.PENDING:
                return format_html(
                    "<div style='display:inline-block; background-color: yellow; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                    obj.extended_status,
                )

            return format_html(
                "<div style='display:inline-block; background-color: gray; color: white; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                obj.extended_status,
            )

    colorized_status.short_description = "status"

    def source_type(self, obj=None):

        if obj and obj.card:
            return f"card ends with {obj.card.last_digits}"

        if obj and obj.source:
            return obj.source.get_type_display()


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


class OccurrenceInline(admin.TabularInline):
    model = Occurrence

    extra = 0

    show_change_link = True

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "colorized_status",
        "livemode",
        "date_created",
        "date_updated",
        "deleted",
        "active",
        "every",
        "in_words",
        "period",
        "start_on",
    )
    list_filter = (
        "livemode",
        "date_created",
        "date_updated",
        "deleted",
        "active",
    )

    fields = [
        "id",
        "livemode",
        "data",
        "deleted",
        "active",
        "charge",
        "charge_amount",
        "end_on",
        "ended_at",
        "every",
        "in_words",
        "next_occurrences_on",
        "period",
        "start_on",
        "status",
    ]

    read_only_fields = [
        "colorized_status",
    ]

    search_fields = [
        "id",
        "charge__customer__user__username",
        "charge__customer__user__email",
    ]

    inlines = [
        ChargeInline,
        OccurrenceInline,
    ]

    def colorized_status(self, obj=None):
        if obj:
            if obj.status == ScheduleStatus.RUNNING:
                return format_html(
                    "<div style='display:inline-block; background-color: green; color: white; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                    obj.status,
                )

            if obj.status == ScheduleStatus.EXPIRING:
                return format_html(
                    "<div style='display:inline-block; background-color: yellow; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                    obj.status,
                )

            if obj.status == ScheduleStatus.EXPIRED:
                return format_html(
                    "<div style='display:inline-block; background-color: gray; color: white; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                    obj.status,
                )

            if obj.status in [ScheduleStatus.DELETED, ScheduleStatus.SUSPENDED]:
                return format_html(
                    "<div style='display:inline-block; background-color: gray; color: white; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                    obj.status,
                )

            return format_html(
                "<div style='display:inline-block; background-color: gray; color: white; padding: 0.25rem; border-radius: 5px;'>{}</div>",
                obj.status,
            )

    colorized_status.short_description = "Status"

    def has_change_permission(self, request, obj=None):
        return False

    def charge_amount(self, obj=None):
        if obj and obj.charge:
            return f"{obj.charge.human_amount} {obj.charge.currency}"


@admin.register(Occurrence)
class OccurrenceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "livemode",
        "date_created",
        "date_updated",
        "message",
        "processed_at",
        "retry_on",
        "schedule",
        "schduled_on",
        "status",
    )
    list_filter = (
        "livemode",
        "date_created",
        "date_updated",
        "processed_at",
        "retry_on",
        "schedule",
        "schduled_on",
    )

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ChargeSchedule)
class ChargeScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "livemode",
        "date_created",
        "date_updated",
        "amount",
        "currency",
        "card",
        "customer",
        "default_card",
    )
    list_filter = (
        "livemode",
        "date_created",
        "date_updated",
        "default_card",
    )

    def has_change_permission(self, request, obj=None):
        return False
