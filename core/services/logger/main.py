from typing import Any, Dict, Optional

import after_response

from core.services.after.main import AfterResponseService
from src.settings.logger import LOG_CONFIG
from utilities.time import utc_datetime

logger = LOG_CONFIG.logger

class DokoolaLoggerService:
    """Enhanced logging class with structured logging support"""

    lazy: "DokoolaLazyLoggerService" = None # type: ignore

    @staticmethod
    def __enrich_extras(extras: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enrich log extras with common fields"""
        enriched = extras or {}
        enriched.update(
            {
                "app_id": LOG_CONFIG.app_id,
                "environment": LOG_CONFIG.runtime_environment,
                "timestamp": utc_datetime().__str__(),
            }
        )
        return enriched

    @classmethod
    def __log(
        cls, log_attr: str, message: Any, extras: Optional[Dict[str, Any]] = None
    ) -> None:
        """Internal logging method with structured data support"""
        _after_response = False
        enriched_extras = cls.__enrich_extras(extras)

        if extras and "after_response" in extras:
            _after_response = True
            extras.pop("after_response")

        if isinstance(message, dict):
            extras = extras or message
            enriched_extras.update(message)

            if "after_response" in message:
                _after_response = True
                message.pop("after_response")

            log_method = None

            if not hasattr(logger, log_attr.lower()):
                return None

            log_method = getattr(logger, log_attr.lower())

            if _after_response:
                AfterResponseService.schedule_after(
                    log_method, message, enriched_extras
                )
                return

            AfterResponseService.schedule_task(
                lambda: log_method(message, extra=enriched_extras)
            )

    @classmethod
    def debug(cls, message: Any, extra: Optional[Dict[str, Any]] = None) -> None:
        return cls.__log("debug", message, extra)

    @classmethod
    def info(cls, message: Any, extra: Optional[Dict[str, Any]] = None) -> None:
        return cls.__log("info", message, extra)

    @classmethod
    def warning(cls, message: Any, extra: Optional[Dict[str, Any]] = None) -> None:
        return cls.__log("warning", message, extra)

    @classmethod
    def error(cls, message: Any, extra: Optional[Dict[str, Any]] = None) -> None:
        return cls.__log("error", message, extra)

    @classmethod
    def critical(cls, message: Any, extra: Optional[Dict[str, Any]] = None) -> None:
        return cls.__log("critical", message, extra)

    @classmethod
    def exception(cls, message: Any, extra: Optional[Dict[str, Any]] = None) -> None:
        return cls.__log("exception", message, extra)


class DokoolaLazyLoggerService(DokoolaLoggerService):

    def __init__(self, lazy=False):
        super().__init__()
        self.is_lazy = lazy

    @classmethod
    def _log(
        cls, log_attr: str, message: Any, extras: Optional[Dict[str, Any]] = None
    ) -> None:

        # return cls.__log(log_attr, message, extras)
        pass


DokoolaLoggerService.lazy = DokoolaLazyLoggerService(lazy=True)
__all__ = ["DokoolaLoggerService"]
