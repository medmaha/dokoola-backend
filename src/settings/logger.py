import logging
import logging.config
import os


class LogConfig:
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s]: %(message)s"},
            "detailed": {"format": "%(asctime)s [%(levelname)s] %(message)s"},
        },
        "handlers": {},
        "loggers": {},
    }

    def __init__(self):
        from src.settings.shared import APPLICATION_IDENTIFIER, RUNTIME_ENVIRONMENT

        self.logger = logging.getLogger("dokoola")
        self.app_id = APPLICATION_IDENTIFIER
        self.runtime_environment = RUNTIME_ENVIRONMENT
        self.console_log_allowed = bool(int(os.getenv("DKL-CONSOLE-LOG", "0")))
        LogConfig._setup_logging(self)

        logging.info(
            "Server up and running",
            extra={
                "Env": self.runtime_environment,
                "App": self.app_id,
                "Console-LOG": self.console_log_allowed,
            },
        )

    @classmethod
    def _setup_logging(cls, self: "LogConfig") -> None:
        """Configure logging based on environment"""
        logging.config.dictConfig(self.LOGGING_CONFIG)

        self._setup_console_logging()

        if self.runtime_environment == "development":
            self._setup_development_logging()
        else:
            self._setup_production_logging()

        self.logger.setLevel(logging.DEBUG)

    def _setup_console_logging(self) -> None:
        """Setup console logging"""
        if self.console_log_allowed:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(
                logging.Formatter(
                    self.LOGGING_CONFIG["formatters"]["detailed"]["format"]
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
            logging.Formatter(self.LOGGING_CONFIG["formatters"]["detailed"]["format"])
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
                    self.LOGGING_CONFIG["formatters"]["standard"]["format"]
                )
            )
            logtail_handler.setLevel(logging.INFO)
            self.logger.addHandler(logtail_handler)


__all__ = ["LogConfig"]


LOG_CONFIG = LogConfig()
