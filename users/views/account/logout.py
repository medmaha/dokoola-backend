from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from users.views.account.auth_token import GenerateToken


class LogoutView(GenericAPIView):
    """A view for logging out the request.user's Access and Refresh tokens"""

    jwt_token_generator = GenerateToken()

    def get_serializer_class(self):
        return self.jwt_token_generator.serializer_class

    def post(self, request, *args, **kwargs):
        try:
            # get the refresh token from the request
            refresh_token = RefreshToken(request.data["refresh"])
            # delete the refresh token (and associated access token)
            refresh_token.blacklist()
            request.user.online = False
            request.user.save()
        except TokenError:
            pass
        return Response({"success": True}, status=200)
