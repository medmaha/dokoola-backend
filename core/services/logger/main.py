from typing import Any, Dict, Optional

from core.services.after.main import AfterResponseService

from src.settings.shared import LOG_CONFIG

class DokoolaLoggerService:
    """Enhanced logging class with structured logging support"""

    @staticmethod
    def _enrich_extras(extras: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enrich log extras with common fields"""
        enriched = extras or {}
        enriched.update(
            {"APP_ID": LOG_CONFIG.app_id, "ENVIRONMENT": LOG_CONFIG.runtime_environment}
        )
        return enriched

    @classmethod
    def _log(
        cls, log_attr: str, message: Any, extras: Optional[Dict[str, Any]] = None
    ) -> None:
        """Internal logging method with structured data support"""
        enriched_extras = cls._enrich_extras(extras)

        if isinstance(message, dict):
            extras = extras or message
            enriched_extras.update(message)

        AfterResponseService.schedule_log(
            lambda: getattr(LOG_CONFIG.logger, log_attr)(
                message if not isinstance(message, dict) else str(message),
                extra=enriched_extras,
            )
        )

    @classmethod
    def debug(cls, message: Any, extra: Optional[Dict[str, Any]] = None) -> None:
        cls._log("debug", message, extra)

    @classmethod
    def info(cls, message: Any, extra: Optional[Dict[str, Any]] = None) -> None:
        cls._log("info", message, extra)

    @classmethod
    def warning(cls, message: Any, extra: Optional[Dict[str, Any]] = None) -> None:
        cls._log("warning", message, extra)

    @classmethod
    def error(cls, message: Any, extra: Optional[Dict[str, Any]] = None) -> None:
        cls._log("error", message, extra)

    @classmethod
    def critical(cls, message: Any, extra: Optional[Dict[str, Any]] = None) -> None:
        cls._log("critical", message, extra)


__all__ = ["DokoolaLoggerService"]
