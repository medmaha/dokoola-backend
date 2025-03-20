from django.db import models, transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from users.models import User
from utilities.generator import get_serializer_error_message

from ..models import Certificate, Talent
from ..serializers import (
    TalentCertificateReadSerializer,
    TalentCertificateWriteSerializer,
)

MAX_CERTIFICATE_COUNT = 6


class TalentCertificateAPIView(GenericAPIView):
    serializer_class = TalentCertificateReadSerializer

    def get(self, request, public_id: str, *args, **kwargs):
        try:
            user: User = request.user

            if user.public_id == public_id:
                certificates = Certificate.objects.filter(
                    talent__public_id=public_id
                ).order_by("-date_issued")
            else:
                certificates = Certificate.objects.filter(
                    talent__public_id=public_id, published=True
                ).order_by("-date_issued")

            serializer = self.get_serializer(certificates, many=True)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )

    def post(self, request, public_id: str, *args, **kwargs):
        try:
            user: User = request.user
            profile, profile_type = user.profile

            if profile_type.lower() != "talent":
                return Response({"message": "This request is prohibited"}, status=403)

            serializer = TalentCertificateWriteSerializer(data=request.data)

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
                    _serializer = self.get_serializer(certificate)
                    return Response(_serializer.data, status=201)

                error_message = get_serializer_error_message(
                    serializer.errors, "ERROR! bad request attempted"
                )
                return Response({"message": error_message}, status=400)

        except Exception:
            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )

    def put(self, request, public_id: str, *args, **kwargs):
        try:
            with transaction.atomic():
                certificate_public_id = request.data.get("public_id")
                certificate = Certificate.objects.select_for_update().get(
                    talent__user=request.user,
                    talent__public_id=public_id,
                    public_id=certificate_public_id,
                )

                serializer = TalentCertificateWriteSerializer.merge_serialize(
                    certificate, request.data
                )
                if serializer.is_valid():
                    _cert = serializer.save()
                    _serializer = self.get_serializer(_cert)
                    return Response(_serializer.data, status=200)

                msg = get_serializer_error_message(serializer.errors)
                return Response({"message": msg}, status=400)

        except Certificate.DoesNotExist:
            return Response({"message": "Certificate does not exists"}, status=404)

        except Exception as e:
            # TODO: log error
            return Response({"message": str(e)}, status=500)

    def delete(self, request, public_id: str, *args, **kwargs):
        try:
            with transaction.atomic():
                certificate_public_id = request.data.get("public_id", None)
                certificate = Certificate.objects.get(
                    talent__user=request.user,
                    talent__public_id=public_id,
                    public_id=certificate_public_id,
                )
                certificate.delete()
                return Response(status=204)

        except Certificate.DoesNotExist:
            # TODO: log error
            return Response({"message": "Certificate does not exists"}, status=404)

        except Exception as e:
            # TODO: log error
            return Response({"message": "Bad request attempted"}, status=400)
