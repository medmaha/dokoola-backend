from django.utils.log import  log_response
from django.http import HttpRequest, HttpResponse

import logging
from datetime import  datetime


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

    def __call__(self, request: HttpRequest):

        start_time = datetime.now()
        response: HttpResponse = self.get_response(request)
        timestamp = self.get_timestamp(start_time)
        status_code = response.status_code

        message = (f"\"@{start_time.date()} {str(start_time.time()).split(".")[0]}\" "
                f"{request.method.upper()} - {request.path} - {status_code} - [{timestamp}]") # type: ignore

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
