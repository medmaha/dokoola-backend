from typing import Any, Callable

class _AfterResponseService:
    """Service for managing and executing callbacks after HTTP response"""

    def __init__(self):
        pass

    def schedule_task(
        self, callback: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:

        callback(*args, **kwargs)

    def schedule_log(
        self, callback: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:

        callback()



# Singleton instance
AfterResponseService = _AfterResponseService()
__all__ = ["AfterResponseService"]
