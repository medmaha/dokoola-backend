import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-0l3#19c*dv9r=cfgci3nhnp%8a924d77c8ub++ptddu#@nr_+k"

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "dokoola.onrender.com", "mtoure.pythonanywhere.com"]

AUTH_USER_MODEL = "users.User"

APPEND_SLASH = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django_extensions",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    # "_automation",
    "users",
    "staffs",
    "clients",
    "freelancers",
    "reviews",
    "jobs",
    "proposals",
    "messenging",
    "notifications",
]

REST_FRAMEWORK = {
    "PAGE_SIZE": 15,
    "DEFAULT_PAGINATION_CLASS": "src.features.paginator.DokoolaPaginator",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "src.features.dokoola_auth.DokoolaAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
}

CSRF_COOKIE_AGE = 60 * 30  # 30 minutes
CSRF_TRUSTED_ORIGINS = [
    os.environ.get("FRONTEND_URL"),
    "http://localhost:80",
    "http://localhost:3000",
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
]


# CORS_ALLOWED_ORIGINS = [
#     "https://example.com",
# ]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
    "GET",
    "PUT",
    "UPDATE",
    "PATCH",
    "POST",
    "DELETE",
    "OPTIONS",
)


CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-requested-with",
    "x-token",
    "x-csrftoken",
)

ROOT_URLCONF = "src.urls"

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

WSGI_APPLICATION = "src.wsgi.application"


# DATABASE SETTINGS

DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_ENGINE = os.environ.get("DB_ENGINE")
DB_PASSWORD = os.environ.get("DB_PASSWORD")


def missing_db_credentials():
    credentials = [
        "DB_NAME",
        "DB_USER",
        "DB_HOST",
        "DB_PORT",
        "DB_ENGINE",
        "DB_PASSWORD",
    ]
    message = ""
    for credential in credentials:
        if not os.environ.get(credential):
            message = f"{credential}"
            break

    return f"Missing Database credentials: {message}"


assert DB_ENGINE and DB_USER and DB_HOST and DB_PORT, missing_db_credentials()

DATABASES = {
    # "default": {
    #     "ENGINE": "django.db.backends.sqlite3",
    #     "NAME": "db.sqlite3",
    # },
    "default": {
        "USER": DB_USER,
        "NAME": DB_NAME,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
        "ENGINE": DB_ENGINE,
        "PASSWORD": DB_PASSWORD,
    },
}


# PASSWORD VALIDATORS

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


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(weeks=4),
    "REFRESH_TOKEN_LIFETIME": timedelta(weeks=5),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer", "JWT"),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(weeks=4),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(weeks=5),
}


# EMAIL BACKEND SETTINGS

# EMAIL_SUBJECT_PREFIX = "Dokoola - "
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 0))
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_USE_TLS = bool(int(os.environ.get("EMAIL_USE_TLS", 0)))


assert (
    EMAIL_HOST
    and EMAIL_USER
    and EMAIL_HOST_PASSWORD
    and EMAIL_PORT
    and EMAIL_HOST
    and EMAIL_USE_TLS
), "All EMAIL_Backend* environment variables must be set"


EMAIL_HOST_USER = EMAIL_USER
# EMAIL_HOST_USER = f"Dokoola <{EMAIL_USER}>"
