from django.urls import path, include

from .views import (
    omise_webhook_view,
    ManagePaymentMethodsView,
    PaymentMethodDeleteView,
    OmiseReturnURIView,
    CheckoutView,
)

app_name = "django_omise"

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("return/<uuid:uid>/", OmiseReturnURIView.as_view(), name="return_uri"),
    path("webhook/", omise_webhook_view, name="webhook"),
    path(
        "payment_methods/",
        include(
            [
                path(
                    "",
                    ManagePaymentMethodsView.as_view(),
                    name="manage_payment_methods",
                ),
                path(
                    "delete/<pk>/",
                    PaymentMethodDeleteView.as_view(),
                    name="delete_payment_method",
                ),
            ]
        ),
    ),
]
