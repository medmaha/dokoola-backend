""" A route controller for retrieving user profile. """

from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from clients.serializer import ClientRetrieveSerializer
from talents.serializers import TalentProfileDetailSerializer
from users.models import User


class UserProfileAPIView(RetrieveAPIView):

    def retrieve(self, request, username, *args, **kwargs):

        try:
            user = User.objects.get(username=username)
            profile, profile_name = user.profile
        except:
            return Response(
                {"message": "The userID provided, doesn't match our database"},
                status=404,
            )

        if profile_name.lower() == "talent":
            self.serializer_class = TalentProfileDetailSerializer

        if profile_name.lower() == "client":
            self.serializer_class = ClientRetrieveSerializer

        serializer = self.get_serializer(instance=profile, context={"request": request})

        data = serializer.data
        data["is_client"] = profile.user.is_client
        data["is_talent"] = profile.user.is_talent

        return Response(data, status=200)
