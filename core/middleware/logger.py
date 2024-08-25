import json
import os
from datetime import  datetime
from django.http import HttpRequest, HttpResponse

from django.db.models import QuerySet
from  rest_framework.utils.serializer_helpers import ReturnDict

from src.settings.logger import DokoolaLogger



class DokoolaLoggerMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def get_response_message(self, response):
        if hasattr(response, "data"):
            data = response.data
        elif hasattr(response, "content"):
            data = response.content

        content_type = response.get("content-type")
        
        try:
            
            if content_type == "application/json":
                if isinstance(data, str):
                    return json.loads(data).get("message", response.reason_phrase)

                if isinstance(data, QuerySet):
                    # message = data.get("message")
                    # return message or response.reason_phrase
                    return response.reason_phrase

                if  isinstance(data, ReturnDict):
                    message = data.get("message")
                    return message or response.reason_phrase

                if isinstance(data, dict):
                    message = data.get("message")
                    return message or response.reason_phrase

            if content_type == "text/plain":
                return str(data)[:45]
                
            return response.reason_phrase
        
        except Exception as e:
            return "Something went wrong"
        

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

        if hasattr(response, "ignore_logs") and request.ignore_logs : # type: ignore
            return response
        
        end_time = datetime.now()
        service_name = request.headers.get(os.environ.get('SERVICE_HTTP_HEADER', ""), "UNKNOWN-SERVICE")
        user_agent = self.get_readable_from_user_agent(
            request.META.get('HTTP_USER_AGENT', '')
        )

        log_dict = {
            "path": request.path,
            "method": request.method,
            "absolute_path":request.build_absolute_uri(),
            "duration": self.get_duration(end_time, start_time),
            "timestamp": self.get_timestamp(start_time),
            "status_code": response.status_code,
            "status_message": self.get_response_message(response),
            "user_id":request.user.pk,
            "host":request.META.get("HTTP_HOST"),
            "ip_addr": request.META.get("REMOTE_ADDR"),
            "service_name": service_name,
            "user_agent": user_agent
        }

        if response.status_code in [200, 204, 304, 307]:
            DokoolaLogger.info(log_dict, extra=log_dict)
        elif response.status_code in [401, 404]:
            DokoolaLogger.warn(log_dict, extra=log_dict)
        else:
            DokoolaLogger.error(log_dict, extra=log_dict)
        return response


    def get_duration(self, end_time: datetime, start_time: datetime):

        minutes = end_time.minute - start_time.minute
        seconds = str(end_time.microsecond - start_time.microsecond / 1000)[:3]

        if minutes:
            return f"{minutes}:{seconds}s"
        else:
            return f"{seconds}ms"

    def get_timestamp(self, start_time: datetime):
        return f"{start_time.date()} {str(start_time.time()).split(".")[0]}"
