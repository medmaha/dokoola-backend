import random
import re
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView

from staffs.models import Staff
from clients.models import Client
from clients.serializer import ClientUpdateSerializer
from freelancers.models import Freelancer
from freelancers.serializers import FreelancerUpdateSerializer
from users.models import User

from ..token import GenerateToken
from ..serializer import UserCreateSerializer, UserUpdateSerializer

import re


@api_view(["POST"])
@permission_classes([])
def check_email(request):
    email = request.data.get("email")
    exists = User.objects.filter(email=email).exists()
    return Response(
        {
            "exists": exists,
            "message": "An account with this email already exist"
            if exists
            else "No account with this email",
        }
    )


class SignUpView(APIView):
    permission_classes = ()

    def username_suffix(self, _suffix):
        suffix = random.randrange(10, 999)

        if str(suffix) == _suffix:
            return self.username_suffix(suffix)

        return str(suffix)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        username = data.get("username")
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
        serializer = UserCreateSerializer(data=data)

        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            token_generator = GenerateToken()
            tokens = token_generator.tokens(user, context={"request": request})
            user.set_password(data.get("password", "dokoola"))

            if user.is_staff:
                Staff.objects.get_or_create(user=user)
            if user.is_client:
                Client.objects.get_or_create(user=user)
            if user.is_freelancer:
                Freelancer.objects.get_or_create(user=user)

            return Response(tokens, status=201)

        message = ""

        for error in serializer.errors.items():
            field, text = error[0], error[1][0]

            if re.search(rf"{field}", text, re.IGNORECASE):
                message = text.capitalize()
                break

            message = field.capitalize() + ": " + text
            break

        return Response({"message": message}, status=400)


class SignupUserInformation(UpdateAPIView):
    def update(self, request, *args, **kwargs):
        user: User = request.user

        profile, _ = user.profile

        data = request.data.copy()

        if "avatar" in data and not len(data.get("avatar", "")):
            del data["avatar"]

        if profile:
            username = data.get("username")
            username_exists = User.objects.filter(username=username).exists()

            if username_exists:
                return Response(
                    {"message": "Sorry! this username already exist"}, status=400
                )
            data["is_valid"] = True
            user_data = UserUpdateSerializer(instance=request.user, data=data)

            if user_data.is_valid():
                user_data.save()

            if isinstance(profile, Freelancer):
                serializer = FreelancerUpdateSerializer(instance=profile, data=data)
                if serializer.is_valid():
                    serializer.save()

                    serializer = UserUpdateSerializer(instance=user, data=data)
                    if serializer.is_valid():
                        serializer.save()

                        token_generator = GenerateToken()
                        tokens = token_generator.tokens(
                            user, context={"request": request}
                        )
                        return Response(tokens, status=200)

                return Response(
                    {"message": "Invalid values are passed to the payload"}, status=400
                )

            if isinstance(profile, Client):
                serializer = ClientUpdateSerializer(instance=profile, data=data)
                if serializer.is_valid():
                    serializer.save()

                    serializer = UserUpdateSerializer(instance=user, data=data)
                    if serializer.is_valid():
                        serializer.save()
                        token_generator = GenerateToken()
                        tokens = token_generator.tokens(
                            user, context={"request": request}
                        )
                        return Response(tokens, status=200)

                print(serializer.errors)
                return Response(
                    {"message": "Invalid values are passed to the payload"}, status=400
                )

        return Response({"message": "Request is forbidden/unauthorize"}, status=403)
