from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from users.models import User
from utilities.generator import get_serializer_error_message

from ..models import Education, Talent
from ..serializers import TalentEducationReadSerializer, TalentEducationWriteSerializer

MAX_EDUCATION_COUNT = 3


class TalentEducationAPIView(GenericAPIView):
    serializer_class = TalentEducationReadSerializer

    def get(self, request, public_id: str, *args, **kwargs):
        try:
            user: User = request.user
            if user.public_id == public_id:
                educations = Education.objects.filter(
                    talent__public_id=public_id
                ).order_by("-start_date", "end_date", "published")
            else:
                educations = Education.objects.filter(
                    talent__public_id=public_id, published=True
                ).order_by("-start_date", "end_date")

            serializer = self.get_serializer(educations, many=True)
            return Response(serializer.data, status=200)

        except Talent.DoesNotExist:
            # TODO: log error
            return Response({"message": "This request is prohibited"}, status=403)

        except Exception as e:
            # TODO: log error
            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )

    def post(self, request, public_id: str, *args, **kwargs):
        user: User = request.user
        profile, profile_type = user.profile

        try:
            if profile_type.lower() != "talent":
                return Response({"message": "This request is prohibited"}, status=403)

            serializer = TalentEducationWriteSerializer(data=request.data)

            with transaction.atomic():
                educations_count = profile.education.select_for_update().count()

                if educations_count >= MAX_EDUCATION_COUNT:
                    return Response(
                        {"message": "Maximum number of educations reached"},
                        status=400,
                    )

                if serializer.is_valid():
                    education = serializer.save()
                    profile.education.add(education)
                    _serializer = self.get_serializer(education)
                    return Response(_serializer.data, status=200)

                error_message = get_serializer_error_message(
                    serializer.errors, "ERROR! bad request attempted"
                )
                return Response({"message": error_message}, status=400)

        except Exception as e:
            print("========================================================================")
            print(e)
            print("========================================================================")
            # TODO: log error
            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )

    def put(self, request, public_id: str, *args, **kwargs):
        try:
            with transaction.atomic():
                education_public_id = request.data.get("public_id")
                education = Education.objects.select_for_update().get(
                    talent__user=request.user,
                    talent__public_id=public_id,
                    public_id=education_public_id,
                )
                serializer = TalentEducationWriteSerializer.merge_serialize(
                    education, request.data
                )

                if serializer.is_valid():
                    _education = serializer.save()
                    _serializer = self.get_serializer(_education)
                    return Response(_serializer.data, status=200)

                error_message = get_serializer_error_message(
                    serializer.errors, "ERROR! bad request attempted"
                )
                return Response({"message": error_message}, status=400)

        except Education.DoesNotExist:
            # TODO: log error
            return Response({"message": "This request is prohibited"}, status=403)
        except Exception as e:
            # TODO: log error
            return Response({"message": "Error: Something went wrong!"}, status=500)

    def delete(self, request, public_id: str, *args, **kwargs):
        try:
            education_public_id = request.data.get("public_id", None)
            education = Education.objects.get(
                talent__user=request.user,
                talent__public_id=public_id,
                public_id=education_public_id,
            )
            education.delete()
            return Response(status=204)
        except Education.DoesNotExist:
            # TODO: log error
            return Response({"message": "This request is prohibited"}, status=403)
        except Exception as e:
            # TODO: log error
            return Response({"message": "Bad request attempted"}, status=400)
