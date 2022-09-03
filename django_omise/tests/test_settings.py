DEBUG = True
ROOT_URLCONF = "urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "django_omise",
        "USER": "django_omise",
        "PASSWORD": "django_omise",
        "HOST": "localhost",
        "PORT": "5431",
    }
}

# DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}

USE_TZ = True
TIME_ZONE = "Asia/Bangkok"

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admin",
    "django_omise",
)

SECRET_KEY = "django_tests_secret_key"

OMISE_PUBLIC_KEY = "test_omise_public_key"
OMISE_SECRET_KEY = "test_omise_secret_key"
OMISE_LIVE_MODE = False

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

TEMPLATES = [
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
]
