import os
from datetime import  datetime
from src.settings.logger import DokoolaLogger
from django.http import HttpRequest, HttpResponse



class DokoolaLoggerMiddleware:

    def __init__(self, get_response):
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
        service_name = request.headers.get(os.environ.get('SERVICE_HTTP_HEADER', ""), "UNKNOWN-SERVICE")
        user_agent = self.get_readable_from_user_agent(
            request.META.get('HTTP_USER_AGENT', '')
        )

        log_dict = {
            "path": request.path,
            "user_id":request.META.get("REMOTE_USER"),
            "method": request.method,
            "timestamp": self.get_timestamp(start_time),
            "duration": self.get_duration(start_time),
            "host":request.get_host(),
            "ip_addr": request.META.get("REMOTE_ADDR"),
            "status_code": response.status_code,
            "status_message": response.reason_phrase,
            "service_name": service_name,
            "server_name": request.META.get("SERVER_NAME"),
            "user_agent": user_agent
        }

        if response.status_code in [200, 204, 304, 307]:
            DokoolaLogger.info(log_dict, extra=log_dict)
        elif response.status_code in [401, 404]:
            DokoolaLogger.warn(log_dict, extra=log_dict)
        else:
            DokoolaLogger.error(log_dict, extra=log_dict)
        return response


    def get_duration(self, start_time: datetime):
        end_time = datetime.now()

        minutes = end_time.minute - start_time.minute
        seconds = str(end_time.microsecond - start_time.microsecond / 1000)[:3]

        if minutes:
            return f"{minutes}:{seconds}s"
        else:
            return f"{seconds}ms"

    def get_timestamp(self, start_time: datetime):
        return f"{start_time.date()} {str(start_time.time()).split(".")[0]}"
