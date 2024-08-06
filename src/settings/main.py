import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

from .api import *
from .cors import *
from .db import *
from .email import *
from .jwt import *
from .unfold import *

# DEBUG = bool(int(os.environ.get("DEBUG", 0)))
DEBUG = True

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")

ALLOWED_HOSTS = ["*"]

AUTH_USER_MODEL = "users.User"

APPEND_SLASH = True

INSTALLED_APPS = [
    "unfold", # Third party app

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
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",

    # The core application services and utilities
    "core",

    # Users Account & Profiles apps
    "users",
    "staffs",
    "clients",
    "freelancers",
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
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.logger.DokoolaLoggerMiddleware"
]

# #  Add a request logger middleware class
# if not DEBUG:
#     MIDDLEWARE.append("core.middleware.logger.DokoolaLoggerMiddleware")

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
            ],
        },
    },
]

WSGI_APPLICATION = "src.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
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
STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "public",
]

MEDIA_ROOT = BASE_DIR / "media"
STATIC_ROOT = BASE_DIR / "static"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

