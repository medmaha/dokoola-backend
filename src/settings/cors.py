import os

CSRF_COOKIE_AGE = 60 * 30  # 30 minutes
CSRF_TRUSTED_ORIGINS = [os.environ.get("FRONTEND_URL")]


CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
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
)
