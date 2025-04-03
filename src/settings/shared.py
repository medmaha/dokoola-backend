import os
from typing import Literal

ENVIRONMENT = Literal["development", "production"]

SECRET_KEY = os.environ.get("SECRET_KEY", "invalid_secret_key")

APPLICATION_NAME = "Dokoola PLatform"

RUNTIME_ENVIRONMENT: ENVIRONMENT = os.getenv("ENVIRONMENT", "").lower()

CONSOLE_LOG_ALLOWED = os.getenv("CONSOLE_LOG", None) != "0"

APPLICATION_IDENTIFIER = os.getenv("APPLICATION_ID", None)

DEBUG = int(os.getenv("DEBUG", 0)) > 0
