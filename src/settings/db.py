import os

DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_ENGINE = os.environ.get("DB_ENGINE")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

DEBUG = bool(int(os.environ.get("DEBUG", 0)))

if not DEBUG:
    assert DB_ENGINE and DB_USER and DB_HOST and DB_PORT, "Invalid Database credentials"

default_db = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": "db.sqlite3",
}

if not DEBUG:
    default_db = {
        "USER": DB_USER,
        "NAME": DB_NAME,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
        "ENGINE": DB_ENGINE,
        "PASSWORD": DB_PASSWORD,
    }


DATABASES = {"default": default_db}
