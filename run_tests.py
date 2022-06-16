import django, sys, os
from django.conf import settings
from django_omise.tests import test_settings
from django.conf import global_settings

settings.configure(
    default_settings=global_settings,
    INSTALLED_APPS=test_settings.INSTALLED_APPS,
    SECRET_KEY=test_settings.SECRET_KEY,
    OMISE_PUBLIC_KEY=test_settings.OMISE_PUBLIC_KEY,
    OMISE_SECRET_KEY=test_settings.OMISE_SECRET_KEY,
    OMISE_LIVE_MODE=test_settings.OMISE_LIVE_MODE,
    MIDDLEWARE=test_settings.MIDDLEWARE,
    TEMPLATES=test_settings.TEMPLATES,
    ROOT_URLCONF=test_settings.ROOT_URLCONF,
    DATABASES=test_settings.DATABASES,
    USE_TZ=test_settings.USE_TZ,
    TIME_ZONE=test_settings.TIME_ZONE,
)

try:
    # Django < 1.8
    from django.test.simple import DjangoTestSuiteRunner

    test_runner = DjangoTestSuiteRunner(verbosity=2)
except ImportError:
    # Django >= 1.8
    django.setup()
    from django.test.runner import DiscoverRunner

    test_runner = DiscoverRunner(verbosity=2)

failures = test_runner.run_tests(["django_omise"])
if failures:
    sys.exit(failures)
