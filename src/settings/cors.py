import os

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
    "HEAD",
    "GET",
    "PUT",
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
    os.environ.get("SERVICE_HTTP_HEADER"),
)


__all__ = [
    "CORS_ALLOW_ALL_ORIGINS",
    "CORS_ALLOW_CREDENTIALS",
    "CORS_ALLOW_METHODS",
    "CORS_ALLOW_HEADERS",
]
