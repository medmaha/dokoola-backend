"""A route controller for retrieving profile profile."""

from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from clients.models import Client
from clients.serializer import ClientRetrieveSerializer
from staffs.models import Staff
from talents.models import Talent
from talents.serializers.talent import TalentReadSerializer
from users.models import User


class UserProfileAPIView(RetrieveAPIView):

    metadata = {}

    def get_serializer_class(self):
        profile_type = self.metadata.get("profile_type", "")

        if profile_type.lower() == "talent":
            return TalentReadSerializer
        if profile_type.lower() == "client":
            return ClientRetrieveSerializer
        return TalentReadSerializer

    def get_user(self, public_id: str):
        try:
            user = User.objects.get(username=public_id)
            profile, profile_type = user.profile
            self.metadata.update(
                {
                    "profile_type": profile_type,
                }
            )
            return profile
        except User.DoesNotExist:
            client = Client.objects.get(public_id=public_id)
            self.metadata.update(
                {
                    "profile_type": "Client",
                }
            )
            return client
        except Client.DoesNotExist:
            talent = Talent.objects.get(public_id=public_id)
            self.metadata.update(
                {
                    "profile_type": "Talent",
                }
            )
            return talent
        except Talent.DoesNotExist:
            staff = Staff.objects.get(public_id=public_id)
            self.metadata.update(
                {
                    "profile_type": "Staff",
                }
            )
            return staff
        except Staff.DoesNotExist:
            return None

    def get_user_by_public_id(self, public_id: str):
        profile = self.get_user(public_id)
        return profile

    def retrieve(self, request, public_id: str, *args, **kwargs):
        print("Public_id:", public_id)
        try:
            profile = self.get_user_by_public_id(public_id)
            if not profile:
                return Response(
                    {"message": "The userID provided, doesn't match our database"},
                    status=404,
                )

            serializer = self.get_serializer(
                instance=profile, context={"request": request, "r_type": "detail"}
            )
            data = serializer.data
            data.update(**self.metadata)
            return Response(data, status=200)

        except Exception as e:
            print("Error:", e)
            return Response(
                {"message": "The userID provided, doesn't match our database"},
                status=500,
            )
