import json
import os
from django.http import HttpRequest, HttpResponse
from datetime import  datetime


DOKOOLA_ACCESS_SERVICES = [
    "DOKOOLA-FRONTEND",
    "DOKOOLA-HEALTH-CHECK/Better-Stack",
    "DOKOOLA-HEALTH-CHECK/Github-Actions",
]

class DokoolaCSRFMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

 
    def __call__(self, request: HttpRequest):

        csrf_header = request.headers.get(os.environ.get("SERVICE_HTTP_HEADER", "_"))

        if not csrf_header in DOKOOLA_ACCESS_SERVICES:
            response: HttpResponse = HttpResponse(
                json.dumps({"message": "Dokoola csrf header not found or not allowed"}),
                status=403,
                headers={"Content-Type": "application/json"}
            )

        else:
            response: HttpResponse = self.get_response(request)
        return response

    def get_timestamp(self, start_time: datetime):
        end_time = datetime.now()

        minutes = end_time.minute - start_time.minute
        seconds = str(end_time.microsecond - start_time.microsecond / 1000)[:3]

        if minutes:
            timestamp = f"{minutes}:{seconds}s"
        else:
            timestamp = f"{seconds}ms"

        return timestamp
