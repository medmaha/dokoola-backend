import os

DB_ENGINE = os.environ.get("DB_ENGINE", None)

credentials = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": "db.sqlite3",
}

if DB_ENGINE:
    DB_NAME = os.environ.get("DB_NAME")
    DB_USER = os.environ.get("DB_USER")
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")

    assert DB_USER and DB_HOST and DB_PORT, "Invalid Database credentials"

    credentials = {
        "USER": DB_USER,
        "NAME": DB_NAME,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
        "ENGINE": DB_ENGINE,
        "PASSWORD": DB_PASSWORD,
    }

DATABASES = {"default": credentials}

__all__ = ["DATABASES"]
