
import threading
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class EmailSender():
    def __init__(self, fail_silently=False):
        self._threader = threading
        self._fail_silently = fail_silently

    def _queue(self, start_process, *args, **kwargs):
        try:
            thread = self._threader.Thread(target=start_process, args=args, kwargs=kwargs)
            thread.start()
        except threading.ThreadError:
            start_process(*args, **kwargs)
        except Exception as error:
            # TODO: handle error
            print(error)
            pass


class EmailService(EmailSender):
    def __init__(self, _fail_silently=False):
        super().__init__(_fail_silently)

    def send(self, email, subject, text=None, html_template_name=None, html_template_context=None):
        
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
            from_email=settings.EMAIL_EMAIL_HOST_DOMAIN,
        )

