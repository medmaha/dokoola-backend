import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import (
    JWTAuthentication as JwtAuthentication,
)

from users.models import User


class JWTAuthentication(JwtAuthentication):
    def __init__(self) -> None:
        super().__init__()
        self.name = "JWT AUTH"

    def _authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise AuthenticationFailed("Authorization header not found")

        auth_header_prefix = self._authenticate_header()
        if not auth_header.startswith(auth_header_prefix):
            raise AuthenticationFailed("Authorization header prefix mismatch")

        token = auth_header[len(auth_header_prefix) :].strip()
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        user = User.objects.get(id=payload["user_id"])
        return (user, token)

    def _authenticate_header(self):
        return "JWT", "Dokoola"
