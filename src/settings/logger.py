import os
import logging, logging.config
import after_response

from logtail import LogtailHandler

LOGGING_CONFIG = None

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {},
        "loggers": {},
    }
)

logger = logging.getLogger(__file__)

runtime_environment = os.environ.get("ENVIRONMENT", "development")
console_log_allowed = bool(int(os.environ.get("CONSOLE_LOG", "0")))

APP_ID = os.environ.get("APP_ID", "DEFAULT")

DEVELOPMENT_MODE = runtime_environment.lower() == "development"

if DEVELOPMENT_MODE and console_log_allowed:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

if not DEVELOPMENT_MODE:

    logtail_handler = LogtailHandler(
        source_token=os.getenv("BETTER_STACK_SOURCE_TOKEN")
    )
    logtail_handler.setLevel(logging.INFO)
    logger.addHandler(logtail_handler)


if DEVELOPMENT_MODE:

    if not os.path.exists(".logs"):
        os.makedirs(".logs")

    file_handler = logging.FileHandler(".logs/dokoola.log")
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

logger.setLevel(logging.DEBUG)


@after_response.enable
def execute_log(log_attr, message, extras):
    try:
        logger.__getattribute__(log_attr)(message, extra=extras)
        if extras:
            extras["LEVEL"] = log_attr
            extras["APP_ID"] = APP_ID
            extras["ENVIRONMENT"] = runtime_environment

            try:
                message["LEVEL"] = log_attr
                message["APP_ID"] = APP_ID
                message["ENVIRONMENT"] = runtime_environment
            except:
                pass

            if isinstance(extras, dict):
                extras = extras
            logging.getLogger("logtail").__getattribute__(log_attr)(
                message, extra=extras
            )
    except:
        pass


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
