from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializer import AuthUserSerializer
from users.models import User


class GenerateToken(TokenObtainPairSerializer):
    def get_token(self, user, **kwargs):
        token = self.token_class.for_user(user)
        serialized_data = AuthUserSerializer(user, **kwargs).data

        is_active = False if "init" in kwargs else user.is_active

        token["user"] = {}

        for key, val in serialized_data.items():
            token["user"][str(key)] = val

        token["user"]["is_active"] = is_active

        return token

    def tokens(self, user, **kwargs):
        user = User.objects.get(pk=user.pk)
        token = self.get_token(user, **kwargs)
        data = {"access": str(token.access_token), "refresh": str(token)}
        return data
