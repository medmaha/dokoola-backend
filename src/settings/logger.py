import logging
import logging.config
import os
from typing import Any


class LogConfig:
    
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "dev": {"format": "[%(levelname)s] %(message)s"},
            "prod": {"format": "[%(levelname)s] %(message)s"},
            "console": {"format": "[%(levelname)s]: %(message)s"},
        },
        "handlers": {},
        "loggers": {},
    }

    def __init__(self):
        from src.settings.shared import APPLICATION_IDENTIFIER, RUNTIME_ENVIRONMENT, CONSOLE_LOG_ALLOWED

        self.logger :Any = logging.getLogger("dokoola")

        self.app_id = APPLICATION_IDENTIFIER
        self.console_log_allowed = CONSOLE_LOG_ALLOWED
        self.runtime_environment = RUNTIME_ENVIRONMENT.lower()

        LogConfig._setup_logging(self)

        logging.info(
            "Server up and running",
            extra={
                "App": self.app_id,
                "Environment": self.runtime_environment,
                "Console-Logging": self.console_log_allowed,
            },
        )

    @classmethod
    def _setup_logging(cls, self: "LogConfig") -> None:
        """Configure logging based on environment"""

        logging.config.dictConfig(self.LOGGING_CONFIG)

        if self.console_log_allowed:
            self._setup_console_logging()

        if self.runtime_environment == "development":
            self._setup_development_logging()

        if self.runtime_environment == "production":
            self._setup_production_logging()

        self.logger.setLevel(logging.DEBUG)

    def _setup_console_logging(self) -> None:
        """Setup console logging"""
        if self.console_log_allowed:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(
                logging.Formatter(
                    self.LOGGING_CONFIG["formatters"]["console"]["format"]
                )
            )
            stream_handler.setLevel(logging.INFO)
            self.logger.addHandler(stream_handler)

    def _setup_development_logging(self) -> None:
        """Setup development environment logging"""

        log_dir = ".logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(os.path.join(log_dir, "dokoola.log"))
        file_handler.setFormatter(
            logging.Formatter(self.LOGGING_CONFIG["formatters"]["dev"]["format"])
        )
        file_handler.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    def _setup_production_logging(self) -> None:
        """Setup production environment logging"""

        from logtail import LogtailHandler

        source_token = os.getenv("BETTER_STACK_SOURCE_TOKEN")
        if source_token:
            logtail_handler = LogtailHandler(source_token=source_token)
            logtail_handler.setFormatter(
                logging.Formatter(
                    self.LOGGING_CONFIG["formatters"]["prod"]["format"]
                )
            )
            logtail_handler.setLevel(logging.INFO)
            self.logger.addHandler(logtail_handler)


__all__ = ["LogConfig"]


LOG_CONFIG = LogConfig()
