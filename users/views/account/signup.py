import random
import re

from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from clients.models import Client
from staffs.models import Staff
from talents.models import Talent
from users.models import User
from users.serializer import UserWriteSerializer

from .auth_token import GenerateToken


class SignupAPIView(GenericAPIView):
    permission_classes = ()
    serializer_class = UserWriteSerializer

    def username_suffix(self, _suffix):
        suffix = random.randrange(10, 999)

        if str(suffix) == _suffix:
            return self.username_suffix(suffix)
        return str(suffix)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        username = data.get("username")

        with transaction.atomic():
            while True:
                username_exists = User.objects.filter(username=username).exists()
                if username_exists:
                    _username = re.sub(r"[0-9]", "", username)
                    username = _username + self.username_suffix(
                        username[: len(username) - 3]
                    )
                else:
                    break

            data["username"] = username
            serializer = UserWriteSerializer(data=data)

            if serializer.is_valid():
                user: User = serializer.save()  # type: ignore
                user.is_active = False
                token_generator = GenerateToken()
                tokens = token_generator.tokens(user, init=True, context={"request": request})  # type: ignore
                user.set_password(data.get("password", "dokoola"))

                if user.is_staff:
                    Staff.objects.get_or_create(user=user)
                if user.is_client:
                    Client.objects.get_or_create(user=user)
                if user.is_talent:
                    Talent.objects.get_or_create(user=user)

                # TODO: send a welcome email to the user
                return Response(tokens, status=201)

            message = ""

            for error in serializer.errors.items():  # type: ignore
                field, text = error[0], error[1][0]

                if re.search(rf"{field}", text, re.IGNORECASE):
                    message = text.capitalize()
                    break

                message = field.capitalize() + ": " + text
                break

            return Response({"message": message}, status=400)
