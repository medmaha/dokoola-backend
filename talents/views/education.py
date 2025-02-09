from django.db import models, transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from users.models import User
from utilities.generator import get_serializer_error_message

from ..models import Education, Talent
from ..serializers import (
    TalentEducationSerializer,
)

MAX_EDUCATION_COUNT = 3


class TalentEducationAPIView(GenericAPIView):
    serializer_class = TalentEducationSerializer

    def get(self, request, username: str, *args, **kwargs):
        try:
            user: User = request.user

            if user.username == username:
                educations = (
                    Education.objects
                    .filter(talent__user__username=username)
                    .order_by("-start_date", "end_date", "published")
                )
            else:
                educations = (
                    Education.objects
                    .filter(talent__user__username=username, published=True)
                    .order_by("-start_date")
                )

            serializer = self.get_serializer(educations, many=True)
            return Response(serializer.data, status=200)

        except Talent.DoesNotExist:
            return Response({"message": "This request is prohibited"}, status=403)

        except Exception:
            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )

    def post(self, request, username: str, *args, **kwargs):
        user: User = request.user
        profile, profile_type = user.profile

        if profile_type.lower() != "talent":
            return Response({"message": "This request is prohibited"}, status=403)

        serializer = self.get_serializer(data=request.data)

        try:
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

                    serializer = self.get_serializer(education)
                    return Response(serializer.data, status=200)

                error_message = get_serializer_error_message(
                    serializer.errors, "ERROR! bad request attempted"
                )
                return Response({"message": error_message}, status=400)

        except Exception:
            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )

    def put(self, request, username: str, *args, **kwargs):
        try:
            education = Education.objects.get(id=username, talent__user=request.user)
            serializer = self.get_serializer(instance=education, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            raise Exception(str(serializer.errors))
        except Education.DoesNotExist:
            return Response({"message": "This request is prohibited"}, status=403)
        except Exception as e:
            return Response({"message": str(e)}, status=400)

    def delete(self, request, username: str, *args, **kwargs):
        try:
            user = request.user
            profile, profile_type = user.profile

            if profile_type.lower() != "talent":
                return Response({"message": "This request is prohibited"}, status=403)

            education = profile.education.filter(id=username).delete()

            if not education:
                return Response({"message": "education not found"}, status=404)
            return Response({"message": "education deleted"}, status=200)
        except Education.DoesNotExist:
            return Response({"message": "This request is prohibited"}, status=403)
        except:

            return Response({"message": "Bad request attempted"}, status=400)
