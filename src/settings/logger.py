import os
import logging, logging.config
import after_response

LOGGING_CONFIG = None

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "logtail": {
                "class": "logtail.LogtailHandler",
                "source_token": os.getenv("BETTER_STACK_SOURCE_TOKEN"),
            },
        },
        "loggers": {
            "logtail": {
                "handlers": [
                    "logtail",
                ],
                "level": "INFO",
            },
            "django": {"handlers": [], "level": "INFO", "propagate": False},
        },
    }
)

logger = logging.getLogger(__file__)

runtime_environment = os.environ.get("ENVIRONMENT", "development")

if runtime_environment == "production":
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_formatter = logging.Formatter("%(levelname)s - %(message)s")
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

# File output logger
file_handler = logging.FileHandler(".logs/dokoola.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

logger.setLevel(logging.INFO)


@after_response.enable
def execute_log(log_attr, message, extras):
    try:
        logger.__getattribute__(log_attr)(message, extra=extras)
        if extras:
            logging.getLogger("logtail").__getattribute__(log_attr)(
                message, extra=extras
            )
    except:
        ("Logging Failed!")


class DokoolaLogger:

    @classmethod
    def __log(cls, log_attr, message, extras, after_response=False):
        if after_response:
            execute_log.after_response(log_attr, message, extras)
        else:
            execute_log(log_attr, message, extras)

    @classmethod
    def debug(cls, message, extra: dict | None = None):
        return cls.__log("debug", message, extra)

    @classmethod
    def info(cls, message, extra: dict | None = None, after_response=False):
        return cls.__log("info", message, extra, after_response)

    @classmethod
    def warn(cls, message, extra: dict | None = None, after_response=False):
        return cls.__log("warn", message, extra, after_response)

    @classmethod
    def error(cls, message, extra: dict | None = None, after_response=False):
        return cls.__log("error", message, extra, after_response)

    @classmethod
    def critical(cls, message, extra: dict | None = None, after_response=False):
        return cls.__log("critical", message, extra, after_response)


__all__ = ["DokoolaLogger", "LOGGING_CONFIG"]
