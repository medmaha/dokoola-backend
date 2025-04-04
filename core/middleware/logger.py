import json
import os
from datetime import datetime
from typing import Any, Callable

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from rest_framework.utils.serializer_helpers import ReturnDict

from core.services.logger import DokoolaLoggerService


class DokoolaLoggerMiddleware:
    SLOW_QUERY_THRESHOLD = 0.1  # 100ms
    STATUS_CODE_MAPPINGS = {
        (200, 201, 204, 304, 307): ("INFO", DokoolaLoggerService.info),
        (400, 401, 404): ("WARN", DokoolaLoggerService.warning),
        (500, 503): ("ERROR", DokoolaLoggerService.critical),
        (500, 503): ("CRITICAL", DokoolaLoggerService.critical),
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def _extract_message_from_response(self, response: HttpResponse, data: Any) -> str:
        """Extract message from response data based on content type"""
        content_type = response.get("content-type", "")

        if content_type == "application/json":
            if isinstance(data, str):
                try:
                    return json.loads(data).get("message", response.reason_phrase)
                except json.JSONDecodeError:
                    return response.reason_phrase

            if isinstance(data, (ReturnDict, dict)):
                return data.get("message") or response.reason_phrase

            if isinstance(data, QuerySet):
                return response.reason_phrase

        if content_type == "text/plain":
            return str(data)[:45]

        return response.reason_phrase

    def get_response_message(self, response: HttpResponse) -> str:
        """Get formatted message from response"""
        try:
            data = getattr(response, "data", None) or getattr(response, "content", None)
            return self._extract_message_from_response(response, data)
        except Exception:
            return "Something went wrong"

    def get_readable_from_user_agent(self, user_agent: str) -> str:
        """Get human-friendly version of user agent string"""
        agent = user_agent.lower()

        DEVICE_MAPPINGS = {
            "iphone": "iPhone",
            "ipad": "iPad",
            "android": "Android",
            "windows": "Windows",
            "linux": "Linux",
            "mac": "Mac",
        }

        PLATFORM_MAPPINGS = {
            "edge": "Edge",
            "edg": "Edge",
            "firefox": "Firefox",
            "opera": "Opera",
            "curl": "cURL",
            "postman": "Postman",
            "chrome": "Chrome",
            "safari": "Safari",
        }

        device = next(
            (DEVICE_MAPPINGS[key] for key in DEVICE_MAPPINGS if key in agent),
            "Unknown Device",
        )
        platform = next(
            (PLATFORM_MAPPINGS[key] for key in PLATFORM_MAPPINGS if key in agent),
            "Unknown",
        )

        return f"{device}/{platform}"

    def _get_log_level(self, status_code: int) -> tuple[str, Callable]:
        """Get appropriate log level based on status code"""
        for codes, level_info in self.STATUS_CODE_MAPPINGS.items():
            if status_code in codes:
                return level_info
        return "ERROR", DokoolaLoggerService.error

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and log relevant information"""
        from django.db import connection

        start_time = datetime.now()
        response = self.get_response(request)
        end_time = datetime.now()

        # Skip logging if explicitly ignored
        if getattr(response, "ignore_logs", False) or getattr(
            request, "ignore_logs", False
        ):
            return response

        # Log slow queries
        for query in connection.queries:
            if float(query["time"]) > self.SLOW_QUERY_THRESHOLD:
                DokoolaLoggerService.warning(
                    {
                        "event": "slow_query",
                        "query": query["sql"],
                        "time": query["time"],
                        "path": request.path,
                    }
                )

        # Prepare log data
        service_name = request.headers.get(
            os.environ.get("DKL-SERVICE-NAME", ""), "UNKNOWN-SERVICE"
        )

        log_data = {
            "status": response.status_code,
            "duration": self._format_duration(end_time, start_time),
            "method": request.method,
            "path": request.path,
            "user_id": str(request.user.pk),
            "timestamp": self._format_timestamp(start_time),
            "status_message": self.get_response_message(response),
            "host": request.META.get("HTTP_HOST"),
            "ip_addr": request.META.get("REMOTE_ADDR"),
            "service_name": service_name,
            "consumer_id": request.headers.get("DKL-CONSUMER-ID", None),
            "user_agent": self.get_readable_from_user_agent(
                request.META.get("HTTP_USER_AGENT", "")
            ),
        }

        # Log with appropriate level based on status code
        level, log_func = self._get_log_level(response.status_code)
        log_data["level"] = level
        log_func(log_data)

        return response

    def _format_duration(self, end_time: datetime, start_time: datetime) -> str:
        """Format request duration in a human-readable format"""
        minutes = end_time.minute - start_time.minute
        milliseconds = str((end_time.microsecond - start_time.microsecond) / 1000)[:3]
        return f"{minutes}:{milliseconds}s" if minutes else f"{milliseconds}ms"

    def _format_timestamp(self, timestamp: datetime) -> str:
        """Format timestamp in a consistent format"""
        return f"{timestamp.date()} {str(timestamp.time()).split('.')[0]}"
