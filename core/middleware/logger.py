import logging
from datetime import  datetime
import os

from django.http import HttpRequest, HttpResponse

class Logger:
    def __init__(self):
        logger = logging.getLogger(__file__)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("SERVER %(levelname)s:  %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        self.log = logger

DokoolaLogger = Logger().log

class DokoolaLoggerMiddleware:

    def __init__(self, get_response):
        self.logger = Logger()
        self.get_response = get_response

    def get_readable_from_user_agent(self, user_agent:str):
        # Get the human friendly version for request user-agent

        agent = user_agent.lower()
        platform = "Unknown"
        device="Unknown Device"

        list_devices = ["iphone", "ipad", "android", "windows", "linux", "mac"]
        list_platforms = ["edge", "edg", "firefox", "opera", "edge", "curl", "postman", "chrome",  "safari"]

        for _platform in list_platforms:
            if _platform in agent:
                if _platform == "edg":
                    platform = "Edge"
                else:
                    platform = _platform.capitalize()
                break
        for _device in list_devices:
            if _device in agent:
                device = _device.capitalize()
                break

        return f"{device.capitalize()}/{platform}"
    
    def __call__(self, request: HttpRequest):

        start_time = datetime.now()
        response: HttpResponse = self.get_response(request)

        timestamp = self.get_timestamp(start_time)
        status_code = response.status_code
        service_name = request.headers.get(os.environ.get('SERVICE_HTTP_HEADER', ""), "UNKNOWN-SERVICE")
        req_user_agent = self.get_readable_from_user_agent(
            request.META.get('HTTP_USER_AGENT', '')
        )

        message = (f"[@{start_time.date()} {str(start_time.time()).split(".")[0]} | {timestamp}] "
                f"{status_code} - {request.method.upper()} - {request.path} - {service_name} - [{req_user_agent}]") # type: ignore

        if status_code in [200, 204, 304]:
            self.logger.log.info(message)
        elif status_code in [401, 404]:
            self.logger.log.warning(message)
        else:
            self.logger.log.error(message)

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
