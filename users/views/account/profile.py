""" A route controller for retrieving user profile. """

from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView

from users.models import User
from clients.serializer import ClientProfileDetailSerializer
from freelancers.serializers import FreelancerProfileDetailSerializer


class UserProfileAPIView(RetrieveAPIView):
    def get_queryset(self, username: str):
        try:
            user = User.objects.get(username=username)
            profile, profile_name = user.profile
        except:
            return None
        if profile_name.lower() == "freelancer":
            self.serializer_class = FreelancerProfileDetailSerializer

        if profile_name.lower() == "client":
            self.serializer_class = ClientProfileDetailSerializer

        if not self.serializer_class:
            return None
        return profile

    def retrieve(self, request, username, *args, **kwargs):
        queryset = self.get_queryset(username)
        if not queryset:
            return Response(
                {"message": "The userID provided, doesn't match our database"},
                status=404,
            )
        serializer = self.get_serializer(
            instance=queryset, context={"request": request}
        )
        return Response(serializer.data, status=200)
