from rest_framework.response import Response

from users.views.account.auth_token import GenerateToken
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class LogoutView(APIView):
    """A view for logging out the request.user's Access and Refresh tokens"""

    jwt_token_generator = GenerateToken()

    def post(self, request, *args, **kwargs):
        try:
            # get the refresh token from the request
            refresh_token = RefreshToken(request.data["refresh"])
            # delete the refresh token (and associated access token)
            refresh_token.blacklist()
            request.user.online = False
            request.user.save()
        except TokenError as e:
            pass
        return Response({"success": True}, status=200)
