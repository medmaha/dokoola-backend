from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from jobs.models import Job
from users.models.user import User
from utilities.generator import get_serializer_error_message


class ThirdPartyJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "status",
            "published",
        ]


class ThirdPartyJobAPIView(GenericAPIView):
    """
    API view for managing third-party job listings.

    Allows clients to update the status and publication state of their third-party job postings.
    Requires client authentication and validates that the requesting user has appropriate permissions.
    """

    serializer_class = ThirdPartyJobSerializer

    def get_serializer(self, *args, **kwargs) -> ThirdPartyJobSerializer:
        return self.serializer_class(*args, **kwargs)

    def get_client_id(self, request):
        user: User = request.user

        client, profile_name = user.profile

        if profile_name.lower() != "client":
            raise ValueError("Forbidden Request")

        return client.public_id

    def get_queryset(self, public_id: str, client_id: str):
        queryset = Job.objects.only(
            "id",
            "title",
            "client__public_id",
            "published",
            "status",
            "public_id",
            "is_third_party",
        ).get(client__public_id=client_id, public_id=public_id, is_third_party=True)
        return queryset

    def put(self, request, public_id):
        try:
            client_id = self.get_client_id(request)
            job = self.get_queryset(public_id, client_id)
            serializer = self.get_serializer(data=request.data, instance=job)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    status=204,
                )

            else:
                return Response(
                    {"message": get_serializer_error_message(serializer.errors)},
                    status=400,
                )

        except Job.DoesNotExist:
            return Response(
                {"message": "Job not found"},
                status=404,
            )
        except:
            return Response(
                {"message": "This request is forbidden"},
                status=403,
            )
