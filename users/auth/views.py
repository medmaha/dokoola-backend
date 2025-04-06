from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from users.auth.serializer import AuthUserSerializer
from users.models.user import User

class AuthUserAPIView(RetrieveAPIView):
    serializer_class = AuthUserSerializer

    def get_queryset(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user: User = request.user

        serializer = self.get_serializer(user)
        data = serializer.data
        
        return Response(data, status=200)
