from django.db import transaction, models

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from utilities.generator import get_serializer_error_message

from ..serializers import (
    FreelancerCertificateSerializer,
)


from ..models import Freelancer, Certificate
from users.models import User


MAX_CERTIFICATE_COUNT = 6


class FreelancerCertificateAPIView(GenericAPIView):
    serializer_class = FreelancerCertificateSerializer

    def get(self, request, username: str, *args, **kwargs):
        try:
            user: User = request.user
            profile, profile_type = user.profile

            if profile_type.lower() == "freelancer":
                certificates = profile.certificates.filter(
                    freelancer__user__username=username
                ).order_by("-date_issued")
            else:
                certificates = (
                    Certificate.objects.select_related()
                    .filter(freelancer__user__username=username, published=True)
                    .order_by("-date_issued")
                )

            serializer = self.get_serializer(certificates, many=True)
            return Response(serializer.data, status=200)

        except Freelancer.DoesNotExist:
            return Response({"message": "This request is prohibited"}, status=403)

        except Exception as e:
            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )

    def post(self, request, username: str, *args, **kwargs):
        user: User = request.user
        profile, profile_type = user.profile

        if not profile_type.lower() == "freelancer":
            return Response({"message": "This request is prohibited"}, status=403)

        serializer = self.get_serializer(data=request.data)

        try:
            with transaction.atomic():
                certificates_count = profile.certificates.select_for_update().count()

                if certificates_count >= MAX_CERTIFICATE_COUNT:
                    return Response(
                        {"message": "Maximum number of certificates reached"},
                        status=400,
                    )

                if serializer.is_valid():
                    certificate = serializer.save()
                    profile.certificates.add(certificate)
                    return Response(serializer.data, status=200)

                error_message = get_serializer_error_message(
                    serializer.errors, "ERROR! bad request attempted"
                )
                return Response({"message": error_message}, status=400)
        except Exception as e:

            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )

    def put(self, request, username: str, *args, **kwargs):
        try:
            certificate = Certificate.objects.get(
                id=username, freelancer__user=request.user
            )
            serializer = self.get_serializer(instance=certificate, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            raise Exception(str(serializer.errors))
        except Certificate.DoesNotExist:
            return Response({"message": "This request is prohibited"}, status=403)
        except Exception as e:
            return Response({"message": str(e)}, status=400)

    def delete(self, request, username: str, *args, **kwargs):
        try:
            user = request.user
            profile, profile_type = user.profile

            if profile_type.lower() != "freelancer":
                return Response({"message": "This request is prohibited"}, status=403)

            certificate = profile.certificates.filter(id=username).delete()

            if not certificate:
                return Response({"message": "certificate not found"}, status=404)
            return Response({"message": "certificate deleted"}, status=200)
        except Certificate.DoesNotExist:
            return Response({"message": "This request is prohibited"}, status=403)
        except:

            return Response({"message": "Bad request attempted"}, status=400)
