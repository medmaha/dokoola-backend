""" A route controller for retrieving user profile. """

from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from clients.serializer import ClientRetrieveSerializer
from talents.serializers import TalentProfileDetailSerializer
from users.models import User


class UserProfileAPIView(RetrieveAPIView):

    profile = None
    profile_type = ""

    def get_serializer_class(self):

        if self.profile_type.lower() == "talent":
            return TalentProfileDetailSerializer

        if self.profile_type.lower() == "client":
            return ClientRetrieveSerializer

        return TalentProfileDetailSerializer

    def retrieve(self, request, username: str, *args, **kwargs):

        try:
            user = User.objects.get(username=username)
            profile, profile_name = user.profile

            print(username, profile, profile_name)

            self.profile = profile
            self.profile_type = profile_name or ""
        except Exception as e:
            print(e)
            return Response(
                {"message": "The userID provided, doesn't match our database"},
                status=404,
            )

        serializer = self.get_serializer(instance=profile, context={"request": request})

        data = serializer.data
        data["is_client"] = profile.user.is_client
        data["is_talent"] = profile.user.is_talent

        return Response(data, status=200)
