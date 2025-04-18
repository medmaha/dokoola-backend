import os
from typing import Literal

ENV_TYPE = Literal["test", "development", "production"]

SECRET_KEY = os.environ.get("SECRET_KEY", "invalid_secret_key")

APPLICATION_NAME = "Dokoola PLatform"

env_value = os.getenv("ENVIRONMENT", "None").lower()
if env_value not in ["test", "development", "production"]:
    raise ValueError(f"Invalid ENVIRONMENT value: {env_value}")

ENVIRONMENT: ENV_TYPE = env_value  # type: ignore
RUNTIME_ENVIRONMENT: ENV_TYPE = ENVIRONMENT

CONSOLE_LOG_ALLOWED = not bool(int(os.getenv("CONSOLE_LOG", 0)))

APPLICATION_IDENTIFIER = os.getenv("APPLICATION_ID", None)

DEBUG = bool(int(os.getenv("DEBUG", 0)))
