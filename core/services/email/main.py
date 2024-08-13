import threading
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from src.settings.logger import DokoolaLogger


class EmailSender:
    def __init__(self, fail_silently=False):
        self._threader = threading
        self._fail_silently = fail_silently

    def _queue(self, start_process, *args, **kwargs):
        callback = kwargs.pop("callback", None)

        def _thread():
            start_process(*args, **kwargs)
            if callback:
                callback()

            emails = kwargs.get("recipient_list")
            log_data = {
                "event": "email-sent",
                "email": emails,
                "subject": args[0],
                "content": args[1],
            }
            DokoolaLogger.info(log_data, extra=log_data)

        try:
            thread = self._threader.Thread(target=_thread)
            thread.start()
        except threading.ThreadError:
            _thread()
            return
        except Exception as error:
            # TODO: handle error
            DokoolaLogger.error(error)
            return


class EmailService(EmailSender):
    def __init__(self, _fail_silently=False):
        super().__init__(_fail_silently)

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
            html = render_to_string(html_template_name, html_template_context or {})
            if not text:
                text = strip_tags(html)

        self._queue(
            send_mail,
            subject,
            text,
            html_message=html,
            recipient_list=[email],
            fail_silently=self._fail_silently,
            from_email=settings.EMAIL_HOST_DOMAIN,
            callback=callback,
        )
