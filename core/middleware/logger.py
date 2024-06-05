from django.middleware.common import CommonMiddleware
from django.utils.deprecation import MiddlewareMixin
from django.utils.log import AdminEmailHandler, log_response


class LoggerMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # if hasattr(request, 'user') and request.user.is_authenticated:
        log_response(request, response)
        return response
