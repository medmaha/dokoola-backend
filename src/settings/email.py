import os

EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 0))
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND")
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = bool(int(os.environ.get("EMAIL_USE_TLS", 0)))


assert (
    EMAIL_HOST
    and EMAIL_HOST_USER
    and EMAIL_HOST_PASSWORD
    and EMAIL_PORT
    and EMAIL_USE_TLS
), "All EMAIL_Backend* environment variables must be set"


# EMAIL_HOST_USER = EMAIL_HOST
EMAIL_HOST_DOMAIN = f"Dokoola {EMAIL_HOST_USER}"

__all__ = [
    "EMAIL_HOST",
    "EMAIL_PORT",
    "EMAIL_BACKEND",
    "EMAIL_USE_TLS",
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
    "EMAIL_HOST_DOMAIN",
    # "DEFAULT_FROM_EMAIL"
]
