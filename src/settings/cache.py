import os

REDIS_USERNAME = os.getenv("REDIS_USERNAME", None)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_HOST = os.getenv("REDIS_HOST", None)
REDIS_PORT = int(os.getenv("REDIS_PORT", 0))

CACHES = {
    "default": {
        # "BACKEND": "django.core.cache.backends.redis.RedisCache",
        # "LOCATION": f"redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}",
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "TIMEOUT": 60 * 15,  # 30 minutes
    }
}


__all__ = ("CACHES",)