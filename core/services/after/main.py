from functools import partial
from typing import Any, Callable, List


class _AfterResponseService:
    """Service for managing and executing callbacks after HTTP response"""

    def __init__(self):
        self._callbacks: List[Callable[[], Any]] = []
        self._executed: bool = False

    def _clear(self) -> None:
        """Reset the service state"""
        self._callbacks = []
        self._executed = False

    def _execute_callbacks(self) -> None:
        """Execute all registered callbacks using after_response"""
        import after_response


        if not self._callbacks:
            return

        @after_response.enable
        def run(callbacks: List[Callable[[], Any]]) -> None:
            for callback in callbacks:
                try:
                    callback()
                except Exception as e:
                    # Log error but continue executing other callbacks
                    from src.settings.logger import DokoolaLogger

                    DokoolaLogger.error(
                        {
                            "event": "after_response_callback_error",
                            "error": str(e),
                            "callback": (
                                callback.__name__
                                if hasattr(callback, "__name__")
                                else str(callback)
                            ),
                        }
                    )

        run(self._callbacks)

    def register(self, callback: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """
        Register a callback to be executed after response

        Args:
            callback: Function to be called
            *args: Positional arguments for the callback
            **kwargs: Keyword arguments for the callback
        """
        if self._executed:
            return  # Prevent registering callbacks after execution

        self._callbacks.append(partial(callback, *args, **kwargs))

    def schedule_email(
        self, callback: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:
        """
        Register a callback to be executed after response

        Args:
            callback: Function to be called
            *args: Positional arguments for the callback
            **kwargs: Keyword arguments for the callback
        """
        if self._executed:
            return  # Prevent registering callbacks after execution

        self._callbacks.append(partial(callback, *args, **kwargs))

    def schedule_log(
        self, callback: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:
        """
        Register a callback to be executed after response

        Args:
            callback: Function to be called
            *args: Positional arguments for the callback
            **kwargs: Keyword arguments for the callback
        """

        # immediately call the callback
        callback()

    def execute(self) -> None:
        """Execute callbacks and reset service state"""
        if self._executed:
            return

        self._executed = True
        self._execute_callbacks()
        self._clear()


# Singleton instance
AfterResponseService = _AfterResponseService()

__all__ = ["AfterResponseService"]
