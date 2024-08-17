from types import FunctionType
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import after_response

from src.settings.logger import DokoolaLogger


@after_response.enable
def execute_send_mail(
    subject,
    text,
    fail_silently: bool = False,
    from_email: str | None = None,
    html_message: str | None = None,
    recipient_list: list[str] | None = None,
    callback: FunctionType | None = None,
):
    if not (recipient_list and text and from_email):
        log_data = {
            "event": "email-not-sent",
            "recipient_list": recipient_list,
            "subject": subject,
            "text": text,
            "from_email": from_email,
            "html_message": html_message,
        }
        DokoolaLogger.warn(log_data, extra=log_data, after_response=False)
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
            "emails": emails,
            "subject": subject,
            "content": text,
            "sent": bool(response),
        }
        DokoolaLogger.info(log_data, extra=log_data, after_response=False)
    except Exception as error:
        log_data = {
            "event": "email-not-sent",
            "recipient_list": recipient_list,
            "subject": subject,
            "text": text,
            "from_email": from_email,
            "html_message": html_message,
            "error": error,
        }
        DokoolaLogger.critical(log_data, extra=log_data, after_response=False)
        return


class EmailService:
    def __init__(self, _fail_silently=False):
        self.fail_silently = _fail_silently

    def send(
        self,
        email,
        subject,
        text=None,
        html_template_name=None,
        html_template_context=None,
        callback=None,
    ):

        html = None

        if html_template_name is not None:
            html = render_to_string(
                html_template_name, context=html_template_context or {}
            )

        if not text:
            text = strip_tags(html or "")

        execute_send_mail.after_response(
            subject,
            text,
            html_message=html,
            callback=callback,
            recipient_list=[email],
            fail_silently=self.fail_silently,
            from_email=settings.EMAIL_HOST_DOMAIN,
        )
