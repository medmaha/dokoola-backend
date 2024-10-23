import json
import os
from datetime import datetime

from django.http import HttpRequest, HttpResponse

DOKOOLA_ACCESS_SERVICES = [
    "DOKOOLA-FRONTEND",
    "DOKOOLA-HEALTH-CHECK/Better-Stack",
    "DOKOOLA-HEALTH-CHECK/Github-Actions",
]


class DokoolaCSRFMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def check_if_samesite(self, request: HttpRequest):
        base_url = os.getenv("BASE_URL", "")
        request_url = request.build_absolute_uri()

        if "deployment-check=true" in request_url:
            return True

        # check if request is coming from a browser and not programmatically
        if "HTTP_USER_AGENT" in request.META:
            user_agent = request.META["HTTP_USER_AGENT"]
            if (
                "Chrome" in user_agent
                or "Firefox" in user_agent
                or "Safari" in user_agent
                or "Mozilla" in user_agent
            ) and base_url in request_url:
                return True

        return False

    def __call__(self, request: HttpRequest):

        samesite = self.check_if_samesite(request)
        if samesite:
            request.META[""] = 3
            request.ignore_logs = True  # type: ignore
            return self.get_response(request)

        csrf_header = request.headers.get(os.environ.get("SERVICE_HTTP_HEADER", "___"))

        if csrf_header not in DOKOOLA_ACCESS_SERVICES:
            response: HttpResponse = HttpResponse(
                json.dumps({"message": "Dokoola csrf header not found or not allowed"}),
                status=403,
                headers={"Content-Type": "application/json"},
            )

        else:
            response: HttpResponse = self.get_response(request)
        return response

    def get_timestamp(self, start_time: datetime):
        end_time = datetime.now()

        minutes = end_time.minute - start_time.minute
        seconds = str(end_time.microsecond - start_time.microsecond / 1000)[:3]

        return f"{minutes}:{seconds}s" if minutes else f"{seconds}ms"
