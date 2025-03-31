import re
from datetime import datetime
from types import FunctionType

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from core.processors.base import email_environment
from core.services.after.main import AfterResponseService
from core.services.logger import DokoolaLoggerService
from src.settings.email import EMAIL_HOST_PASSWORD, EMAIL_HOST_USER


def execute_send_mail(
    subject,
    text,
    sender_name: str | None = None,
    fail_silently: bool = False,
    html_message: str | None = None,
    recipient_list: list[str] | None = None,
    callback: FunctionType | None = None,
):

    if sender_name:
        from_email = f"{sender_name} <{EMAIL_HOST_USER}>"
    else:
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
        DokoolaLoggerService.error(log_data, extra=log_data)
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

        log_data = {
            "event": "email-sent",
            "timestamp": datetime.now(),
            "emails": recipient_list,
            "subject": subject,
            "content": text,
            "sent": bool(response),
        }
        DokoolaLoggerService.info(log_data, extra=log_data)
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
        DokoolaLoggerService.critical(log_data, extra=log_data)
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
        sender_name=None,
        html_template_name=None,
        html_template_context=None,
        execute_now=False,
    ):
        """
        A utility function to send an email.

        Args:
            email: The email address to send the email to.
            subject: The subject of the email.
            text: The text of the email.
            callback: A function to call after the email is sent.
            sender_name: The name of the sender.
            html_template_name: The name of the html template to render.
            html_template_context: The context to pass to the html template.
            execute_now: Whether to send the email immediately.
                otherwise email is sent after the http-response is sent.
        Returns:
            None

        """

        html = None

        # If a template is provided, render it
        if html_template_name is not None:

            # Update the context with the email environment
            context = html_template_context or {}
            context.update(email_environment())

            # Render the template
            html = render_to_string(html_template_name, context=context)

        if not text:
            # Attempt to extract the content from the html element with id "__content"
            content = re.search(r'<span id="__content">(.*?)</span>', html, re.DOTALL)
            if content:
                text = strip_tags(content.group(1)).strip()
            else:
                text = strip_tags(html or "").strip()

        # A callback function that sends the email
        def _callback(subject, text):
            execute_send_mail(
                subject,
                text,
                html_message=html,
                sender_name=sender_name,
                recipient_list=[email],
                fail_silently=self.fail_silently,
            )

        # If the email is to be sent immediately, call the callback function
        if execute_now:
            _callback(subject, text)
        else:
            # Register the callback function to be called after the response is sent
            # AfterResponseService.register(
            #     callback,
            #     subject,
            #     text,
            # )
            _callback(subject, text)
