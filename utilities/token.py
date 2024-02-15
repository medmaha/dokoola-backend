from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import User
from users.serializer import UserSerializer

class GenerateToken(TokenObtainPairSerializer):
    def get_token(self, user, **kwargs):
        token = self.token_class.for_user(user)
        return self.generate_token(token, user, **kwargs)


    def generate_token(self, token, user, **kwargs):
        serialized_data = UserSerializer(user, **kwargs).data

        token["user"] = {}

        for key, val in serialized_data.items():
            token["user"][str(key)] = val

        return token

    def tokens(self, user, **kwargs):
        user = User.objects.get(pk=user.pk)
        token = self.get_token(user, **kwargs)

        data = {"access": str(token.access_token), "refresh": str(token)}

        return data
