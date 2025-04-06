"""A route controller for retrieving profile profile."""

from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from clients.serializer import ClientRetrieveSerializer
from talents.serializers.talent import TalentReadSerializer
from users.models import User


class UserProfileAPIView(RetrieveAPIView):

    profile_type = ""

    def get_serializer_class(self, ):
        profile_type = self.profile_type

        if profile_type.lower() == "talent":
            return TalentReadSerializer
        if profile_type.lower() == "client":
            return ClientRetrieveSerializer
        return TalentReadSerializer

    def retrieve(self, request, public_id: str, *args, **kwargs):
        try:
            profile, profile_type = User.get_profile_by_username_or_public_id(public_id)
            if not profile:
                return Response(
                    {"message": "The userID provided, doesn't match our database"},
                    status=404,
                )

            self.profile_type = profile_type
            serializer = self.get_serializer(
                instance=profile, context={"request": request, "r_type": "detail"}
            )

            data = serializer.data
            data.update({
                "profile_type": profile_type
            })
            return Response(data, status=200)

        except Exception as e:
            return Response(
                {"message": "The userID provided, doesn't match our database"},
                status=500,
            )
