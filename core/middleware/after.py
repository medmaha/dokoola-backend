from typing import Any, Callable, Optional

from django.http import HttpRequest, HttpResponse
from django.template.response import SimpleTemplateResponse

from core.services.after.main import AfterResponseService


class DokoolaAfterMiddleware:
    """Middleware for handling after-response operations in Django"""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        """Initialize the middleware with response handler"""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and return response"""
        response = self.get_response(request)

        # Execute after-response tasks for non-template responses (e.g., JSON/API responses)
        # Only execute if it's not a template response to avoid duplicate execution
        if not isinstance(response, SimpleTemplateResponse):
            AfterResponseService.execute()

        return response

    def process_view(
        self,
        request: HttpRequest,
        view_func: Callable,
        view_args: tuple,
        view_kwargs: dict,
    ) -> None:
        """Hook called before view execution"""
        return None

    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        """Handle exceptions during request processing"""
        # Execute after-response tasks even on exceptions
        AfterResponseService.execute()
        return None

    def process_template_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """Execute after-response tasks for template responses"""
        # Handle template responses
        AfterResponseService.execute()
        return response
