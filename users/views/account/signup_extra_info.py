from django.db import transaction
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from clients.models import Client
from clients.serializer import ClientUpdateSerializer
from talents.models import Talent
from talents.serializers import TalentUpdateSerializer
from users.models import User
from users.serializer import UserUpdateSerializer
from utilities.generator import get_serializer_error_message

from .auth_token import GenerateToken


class UserProfileUpdateAPIView(UpdateAPIView):

    def update(self, request, *args, **kwargs):
        user: User = request.user

        profile, profile_name = user.profile

        data = request.data.copy()

        with transaction.atomic():
            if profile:
                username = data.get("username")
                username_exists = (
                    User.objects.select_related()
                    .select_for_update()
                    .filter(username=username)
                    .exclude(id=user.pk)
                    .exists()
                )

                if username_exists:
                    return Response(
                        {"message": "Sorry! this username already exist"},
                        status=400,
                    )
                data["is_valid"] = True
                user_serializer = UserUpdateSerializer.merge_serialize(user, data)

                if user_serializer.is_valid():
                    user_serializer.save()
                else:
                    error_message = get_serializer_error_message(user_serializer.errors)
                    return Response(dict(message=error_message), status=400)

                if isinstance(profile, Talent):
                    profile_serializer = TalentUpdateSerializer.merge_serialize(
                        profile, data
                    )

                if isinstance(profile, Client):
                    profile_serializer = ClientUpdateSerializer.merge_serialize(
                        profile, data
                    )

                if profile_serializer.is_valid():
                    profile_serializer.save()
                    token_generator = GenerateToken()
                    tokens = token_generator.tokens(  # type: ignore
                        user, context={"request": request}
                    )
                    return Response(tokens, status=200)

                error_message = get_serializer_error_message(profile_serializer.errors)
                return Response(dict(message=str(error_message)), status=400)

        return Response({"message": "Request is forbidden/unauthorize"}, status=403)
