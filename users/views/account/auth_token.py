from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User

from ...serializer import AuthUserSerializer


class GenerateToken(TokenObtainPairSerializer):
    def get_token(self, user:User, **kwargs):
        
        token = self.token_class.for_user(user)
        serialized_data = AuthUserSerializer(user, **kwargs).data

        token["user"] = {}
        
        for key, val in serialized_data.items():
            token["user"][str(key)] = val

        return token

    def tokens(self, user, **kwargs):
        user = User.objects.get(pk=user.pk)
        token = self.get_token(user, **kwargs)
        data = {"access": str(token.access_token), "refresh": str(token)}
        return data
