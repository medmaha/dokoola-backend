import random
import re

from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from clients.models import Client
from staffs.models import Staff
from talents.models import Talent
from users.models import User
from users.models.ott import OTT, OTTProxy
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

        try:

            with transaction.atomic():
                email = data.get("email")
                exists = User.objects.select_related("email").filter(email=email).exists()

                if exists:
                    return Response(
                        {"message":  "An account with this email already exist"},
                        status=400,
                    )

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
                    password = data.get("password", User.DEFAULT_PASSWORD)

                    cleaned_data : dict[str, Any] = dict(serializer.validated_data) # type: ignore
                    user: User = User.objects.create_user(
                        **cleaned_data,
                        password=password,
                        is_active=OTTProxy.validate_verified_ott(email),
                        is_talent= request.data.get("is_talent", False) in ["true", True],
                        is_client= request.data.get("is_client", False) in ["true", True],
                        is_staff= request.data.get("is_staff", False) in ["true", True],
                    )
                    profile = None

                    if user.is_staff:
                        profile = Staff.objects.create(user=user)
                    if user.is_client:
                        profile = Client.objects.create(user=user)
                    if user.is_talent:
                        profile = Talent.objects.create(user=user)

                    if not profile:
                        raise ValueError("No associated profile account")

                    token_generator = GenerateToken()
                    tokens = token_generator.tokens(user)
                    user.set_password(data.get("password", User.DEFAULT_PASSWORD))
                    user.save()

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
        except Exception as e:
            print("======================================================")
            print(e)
            print(request.data)
            print("======================================================")
            return Response({"message": "Internal Server Error"}, status=500)


# %10medmaha@DK