from rest_framework.authentication import BaseAuthentication
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model

User = get_user_model()


class SessionAuthentication(BaseAuthentication):
    def __init__(self) -> None:
        super().__init__()
        self.name = "SESSION AUTH"

    def authenticate(self, request):
        session_key = request.COOKIES.get("sessionid")
        if not session_key:
            return None, None

        session = Session.objects.get(session_key=session_key)
        if not session:
            return None, None

        uid = session.get_decoded().get("_auth_user_id")
        if not uid:
            return None, None

        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return None, None

        return (user, session_key)
