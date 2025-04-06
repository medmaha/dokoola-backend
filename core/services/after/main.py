from typing import Any, Callable
import after_response

@after_response.enable
def execute_after_response(callback, *args, **kwargs):
    callback(*args, **kwargs)

class _AfterResponseService:
    """Service for managing and executing callbacks schedule_after HTTP response"""

    def __init__(self):
        pass

    def schedule_task(
        self, callback: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:

        callback(*args, **kwargs)


    def schedule_after(
        self, callback: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:
        execute_after_response.after_response(callback, *args, **kwargs)


# Singleton instance
AfterResponseService = _AfterResponseService()
__all__ = ["AfterResponseService"]
