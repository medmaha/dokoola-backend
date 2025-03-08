
import os

from src.settings.logger import LogConfig

APPLICATION_NAME = "Dokoola PLatform"

DEBUG = bool(int(os.environ.get("DEBUG", 0)))

LOG_CONFIG = LogConfig()
