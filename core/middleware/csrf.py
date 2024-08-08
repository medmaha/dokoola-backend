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


    def check_if_samesite(self, request: HttpRequest):
        # Check if the request is from the same domain
        print(request.META.get("REMOTE_HOST"))

        host = request.META.get("HTTP_HOST", "00")
        
        base_url = request.META.get("BASE_URL", "")
        if host in base_url:
            return True

        allowed_host = request.META.get("ALLOWED_HOSTS")
        if host in allowed_host:
            return True
        else:
            return False

 
    def __call__(self, request: HttpRequest):
        samesite = self.check_if_samesite(request)

        if samesite:
            print("Same site: Request from same domain")
            return self.get_response(request)

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
