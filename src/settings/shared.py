import os

APPLICATION_NAME = "Dokoola PLatform"

RUNTIME_ENVIRONMENT = os.getenv("ENVIRONMENT", None)
APPLICATION_IDENTIFIER = os.getenv("APPLICATION_ID", None)

DEBUG = int(os.getenv("DEBUG", 0)) > 0
