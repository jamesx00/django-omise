import django, sys, os
from django.conf import settings

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

settings.configure(
    DEBUG=True,
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
        }
    },
    ROOT_URLCONF="django_omise.urls",
    INSTALLED_APPS=(
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.admin",
        "django_omise",
    ),
    SECRET_KEY="django_tests_secret_key",
    OMISE_PUBLIC_KEY="test_omise_public_key",
    OMISE_SECRET_KEY="test_omise_secret_key",
    OMISE_LIVE_MODE=False,
    MIDDLEWARE=(
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ),
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ],
)

try:
    # Django < 1.8
    from django.test.simple import DjangoTestSuiteRunner

    test_runner = DjangoTestSuiteRunner(verbosity=1)
except ImportError:
    # Django >= 1.8
    django.setup()
    from django.test.runner import DiscoverRunner

    test_runner = DiscoverRunner(verbosity=1)

failures = test_runner.run_tests(["django_omise"])
if failures:
    sys.exit(failures)
