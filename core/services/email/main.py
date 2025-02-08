from datetime import datetime
from types import FunctionType

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from src.settings.logger import DokoolaLogger
from src.settings.email import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from core.services.after.main import AfterResponseService


def execute_send_mail(
    subject,
    text,
    fail_silently: bool = False,
    html_message: str | None = None,
    recipient_list: list[str] | None = None,
    callback: FunctionType | None = None,
):
    from_email = f"{settings.APPLICATION_NAME} <{EMAIL_HOST_USER}>"

    if not (recipient_list and text):
        log_data = {
            "event": "email-not-sent",
            "timestamp": datetime.now(),
            "recipient_list": recipient_list,
            "subject": subject,
            "text": text,
            "from_email": from_email,
            "html_message": html_message,
        }
        DokoolaLogger.warn(log_data, extra=log_data)
        return

    try:

        response = send_mail(
            subject=subject,
            message=text,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=fail_silently,
            html_message=html_message,
        )
        if callback:
            callback()

        emails = recipient_list
        log_data = {
            "event": "email-sent",
            "timestamp": datetime.now(),
            "emails": emails,
            "subject": subject,
            "content": text,
            "sent": bool(response),
        }
        DokoolaLogger.info(log_data, extra=log_data)
        return
    except Exception as error:
        log_data = {
            "event": "email-not-sent",
            "timestamp": datetime.now(),
            "recipient_list": recipient_list,
            "subject": subject,
            "text": text,
            "from_email": from_email,
            "html_message": html_message,
            "error": error,
        }
        DokoolaLogger.critical(log_data, extra=log_data)
        return


class EmailService:
    def __init__(self, _fail_silently=False):
        self.fail_silently = _fail_silently

    def send(
        self,
        email,
        subject,
        text=None,
        callback=None,
        html_template_name=None,
        html_template_context=None,
    ):

        html = None

        if html_template_name is not None:
            html = render_to_string(
                html_template_name, context=html_template_context or {}
            )

        if not text:
            text = strip_tags(html or "")

        def callback(subject, text):
            execute_send_mail(
                subject,
                text,
                html_message=html,
                recipient_list=[email],
                fail_silently=self.fail_silently,
            )

        AfterResponseService.register(
            callback,
            subject,
            text,
        )
