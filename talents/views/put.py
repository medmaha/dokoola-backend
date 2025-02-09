from rest_framework.generics import (
    GenericAPIView,
)
from rest_framework.response import Response

from users.serializer import UserUpdateSerializer
from users.views.account.auth_token import GenerateToken
from utilities.generator import get_serializer_error_message

from ..models import Talent
from ..serializers import (
    TalentUpdateDataSerializer,
    TalentUpdateSerializer,
)


class TalentUpdateAPIView(GenericAPIView):
    """
    This view is used for the client mini api view
    Retrieves clients updatable information
    """

    permission_classes = []

    def get(self, request, username, **kwargs):
        self.serializer_class = TalentUpdateDataSerializer
        try:
            talent = Talent.objects.get(user__username=username)
            talent_serializer: TalentUpdateDataSerializer = self.get_serializer(
                instance=talent, context={"request": request}
            )

            return Response(talent_serializer.data, status=200)
        except Talent.DoesNotExist:
            return Response(
                {"message": "Error: User doesn't exist!"},
                status=404,
            )

    def put(self, request, username, **kwargs):
        try:
            talent = Talent.objects.get(user__username=username)
            talent_serializer = TalentUpdateSerializer.merge_serialize(
                talent, request.data, context={"request": request}
            )

            if not talent_serializer.is_valid():
                msg = get_serializer_error_message(
                    talent_serializer, "Talent serializer"
                )
                # raised the same error as the serializer
                return Response({"message": msg}, status=400)

            user_serializer = UserUpdateSerializer.merge_serialize(
                talent.user, request.data, context={"request": request}
            )

            if not user_serializer.is_valid():
                print(user_serializer.errors)
                # raised the same error as the serializer
                msg = get_serializer_error_message(user_serializer, "User serializer")
                # raised the same error as the serializer
                return Response({"message": msg}, status=400)

            updated_user = user_serializer.save()
            talent_serializer.save()

            if updated_user.username != request.user.username:
                token = GenerateToken().tokens(updated_user, init=True)
                return Response(
                    {
                        "tokens": token,
                        "message": "User updated successfully",
                    },
                    status=200,
                )
            return Response(talent_serializer.data, status=200)
        except Talent.DoesNotExist:
            return Response(
                {"message": "Error: User doesn't exist!"},
                status=404,
            )
        except Exception:

            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )
