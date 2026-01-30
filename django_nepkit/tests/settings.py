"""
Django settings for django-nepkit tests.
"""

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django_nepkit",
    "django_nepkit.tests",
]

SECRET_KEY = "test-secret-key-for-django-nepkit"

USE_TZ = True

ROOT_URLCONF = "django_nepkit.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]

NEPKIT = {
    "DEFAULT_LANGUAGE": "en",
    "ADMIN_DATEPICKER": True,
    "TIME_FORMAT": 12,
    "DATE_INPUT_FORMATS": ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"],
}
