from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication


class DokoolaAuthentication(JWTAuthentication):
    def authenticate(self, request):
        session_auth = SessionAuthentication()

        user = session_auth.authenticate(request)

        if user:
            return user

        return super().authenticate(request)
