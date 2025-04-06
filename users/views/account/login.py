from typing import Any

from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.views.account.auth_token import GenerateToken


class LoginView(TokenObtainPairView):
    """A view for getting access token and refreshing tokens"""

    jwt_token_generator = GenerateToken()

    def post(self, request: Any, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        user = User.objects.filter(email=email).first()
        if user:
            if not user.is_active:
                print("============================================================")
                print(email, password, user, user.is_active)
                print("============================================================")
                return Response({"message": "Oops! your account is not activated"}, status=400)
            
            auth = user.check_password(password)
            
            if auth:
                auth_tokens = self.jwt_token_generator.tokens(
                    user, context={"request": request}
                )

                if auth_tokens:
                    user.save()
                    message = f"Welcome back {user.name or user.username}"  # type: ignore
                    return Response(
                        {"tokens": auth_tokens, "message": message},
                        status=200,
                    )

                return Response(
                    {
                        "message": "Uncaught error occurred. Hang tide, we're working on it."
                    },
                    status=500,
                )

        return Response({"message": "Invalid credentials"}, status=400)
