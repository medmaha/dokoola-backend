"""A route controller for retrieving user profile."""

from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from staffs.models import Staff
from clients.models import Client
from talents.models import Talent
from clients.serializer import ClientRetrieveSerializer
from talents.serializers import TalentProfileDetailSerializer
from users.models import User


class UserProfileAPIView(RetrieveAPIView):

    profile = None
    is_staff = False
    is_client = False
    is_talent = False
    profile_type = ""

    def get_serializer_class(self):

        if self.profile_type.lower() == "talent":
            return TalentProfileDetailSerializer

        if self.profile_type.lower() == "client":
            return ClientRetrieveSerializer

        return TalentProfileDetailSerializer

    def get_user(self, username: str):
        try:
            user = User.objects.get(username=username)
            profile, profile_type = user.profile

            if profile_type.lower() == "client":
                self.is_client = True
                self.profile_type = profile_type
            elif profile_type.lower() == "talent":
                self.is_talent = True
                self.profile_type = profile_type
            elif profile_type.lower() == "staff":
                self.is_staff = True
                self.profile_type = profile_type

            return profile

        except User.DoesNotExist:
            return None

    def get_client(self, public_id: str):
        try:
            self.is_client = True
            self.profile_type = "Client"
            return Client.objects.get(public_id=public_id)
        except Client.DoesNotExist:
            return None

    def get_talent(self, public_id: str):
        try:
            self.is_talent = True
            self.profile_type = "Talent"
            return Talent.objects.get(public_id=public_id)
        except Talent.DoesNotExist:
            return None

    def get_staff(self, username: str):
        try:
            self.is_staff = True
            self.profile_type = "Staff"
            return Staff.objects.get(username=username)
        except Staff.DoesNotExist:
            return None

    def get_user_by_public_id(self, public_id: str):
        try:
            user = (
                self.get_user(public_id)
                or self.get_talent(public_id)
                or self.get_client(public_id)
                or self.get_staff(public_id)
            )

            if not user:
                return None

            self.profile = user
            return user
        except:
            return None

    def retrieve(self, request, public_id: str, *args, **kwargs):

        try:
            user = self.get_user_by_public_id(public_id)

            if not user:
                return Response(
                    {"message": "The userID provided, doesn't match our database"},
                    status=404,
                )

        except Exception as e:
            return Response(
                {"message": "The userID provided, doesn't match our database"},
                status=404,
            )

        serializer = self.get_serializer(
            instance=self.profile, context={"request": request}
        )

        data = serializer.data
        data["is_client"] = self.is_client
        data["is_talent"] = self.is_talent
        data["is_staff"] = self.is_staff

        return Response(data, status=200)
