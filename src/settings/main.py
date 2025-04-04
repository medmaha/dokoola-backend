import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from src.settings.shared import APPLICATION_NAME, DEBUG, SECRET_KEY

from .api import REST_FRAMEWORK
from .cors import (
    CORS_ALLOW_ALL_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_HEADERS,
    CORS_ALLOW_METHODS,
)
from .db import DATABASES
from .email import (
    EMAIL_BACKEND,
    EMAIL_HOST,
    EMAIL_HOST_PASSWORD,
    EMAIL_HOST_USER,
    EMAIL_PORT,
    EMAIL_USE_TLS,
)
from .jwt import SIMPLE_JWT
from .logger import LOG_CONFIG
from .unfold import UNFOLD
from .whitenoice import STORAGES

ALLOWED_HOSTS = list(
    set(
        [
            host.strip() if host != "" else "localhost"
            for host in os.getenv("ALLOWED_HOSTS", "").split(",")
        ]
    )
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")

AUTH_USER_MODEL = "users.User"

APPEND_SLASH = True

INSTALLED_APPS = [
    "unfold",  # Third party app
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "corsheaders",
    "rest_framework",
    "after_response",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    # The core application services and utilities
    "core",
    # Users Account & Profiles apps
    "users",
    "staffs",
    "clients",
    "talents",
    "reviews",
    # Projects & Contracts apps
    "jobs",
    "proposals",
    "contracts",
    "projects",
    # Messaging & Notifications apps
    "messaging",
    "notifications",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "core.middleware.logger.DokoolaLoggerMiddleware",
    # "core.middleware.aftar.DokoolaAfterMiddleware",
    # "core.middleware.csrf.DokoolaCSRFMiddleware",
]

# if DEBUG:
#     INSTALLED_APPS.append("silk")
#     INSTALLED_APPS.append("drf_spectacular")
#     INSTALLED_APPS.append("drf_spectacular_sidecar")
#     MIDDLEWARE.append("silk.middleware.SilkyMiddleware")

#     from .spectacular import SPECTACULAR_SETTINGS

#     REST_FRAMEWORK.update(
#         {
#             "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
#         }
#     )


ROOT_URLCONF = "src.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.processors.base.application_environment",
            ],
        },
    },
]

WSGI_APPLICATION = "src.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "GMT"

USE_I18N = True

USE_TZ = True

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [
    BASE_DIR / "public",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
