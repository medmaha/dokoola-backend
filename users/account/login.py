from typing import Any
from rest_framework.response import Response
from django.contrib.auth import authenticate, login

from users.token import GenerateToken
from rest_framework_simplejwt.views import TokenObtainPairView
from ..models import User


class LoginView(TokenObtainPairView):
    """A view for getting access token and refreshing tokens"""

    # authentication_classes = []
    # permission_classes = []

    jwt_token_generator = GenerateToken()

    def post(self, request: Any, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        user = User.objects.filter(email=email).first()
        print(user)
        if user:
            auth = user.check_password(password)
            if auth:
                auth_tokens = self.jwt_token_generator.tokens(
                    user, context={"request": request}
                )

                if auth_tokens:
                    user.save()
                    message = f"Welcome back {user.name or user.username}"  # type: ignore
                    return Response(
                        {"tokens": auth_tokens, "message": message}, status=200
                    )

                return Response(
                    {
                        "message": "Uncaught error occurred. Hang tide, we're working on it."
                    },
                    status=500,
                )

        return Response({"message": "Invalid credentials"}, status=400)
