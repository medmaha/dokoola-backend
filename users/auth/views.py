from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from users.auth.serializer import AuthUserSerializer


class AuthUserAPIView(RetrieveAPIView):
    serializer_class = AuthUserSerializer

    def get_queryset(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user = self.get_queryset()
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=200)
