from django.conf.urls import include
from django.urls import path
from django.contrib import admin

urlpatterns = [
    path("payments/", include("django_omise.urls")),
]