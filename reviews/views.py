from typing import Any

from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from clients.models import Client
from staffs.models import Staff
from talents.models import Talent
from users.models import User
from utilities.generator import get_serializer_error_message

from .models import Review
from .serializer import ReviewReadSerializer, ReviewWriteSerializer


class ReviewsGenericAPIView(GenericAPIView):
    serializer_class = ReviewReadSerializer

    def get_profile_and_profile_type(self, public_id: str):
        """Gets the profile account for given public_id/username"""

        profile_type = ""
        profile = None
        try:
            profile = Client.objects.only("id", "reviews").get(public_id=public_id)
            profile_type = "Client"
        except Client.DoesNotExist:
            profile = Talent.objects.only("id", "reviews").get(public_id=public_id)
            profile_type = "Talent"
        except Talent.DoesNotExist:
            profile = Staff.objects.only("id", "reviews").get(public_id=public_id)
            profile_type = "Staff"
        except Staff.DoesNotExist:
            user = User.objects.get(username=public_id)
            profile, profile_type = user.profile
        except User.DoesNotExist:
            return (None, "")

        return (profile, profile_type)

    def get(self, request, public_id: str, *args, **kwargs):
        try:
            profile, profile_type = self.get_profile_and_profile_type(public_id)
            print(profile, profile_type)
            if not profile:
                return Response({"message": "Profile does not exists"}, status=404)

            queryset = profile.reviews.filter(is_valid=True).order_by("-created_at")
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            # TODO: log error
            return Response({"message": "Internal Server Error"}, status=403)

    def post(self, request, public_id, *args, **kwargs):
        try:
            assert public_id != request.user.public_id, "403 forbidden request!"
            with transaction.atomic():
                profile, profile_type = self.get_profile_and_profile_type(public_id)

                if not profile:
                    return Response({"message": "Profile does not exists"}, status=404)

                serializer = ReviewWriteSerializer(data=request.data)
                if serializer.is_valid():
                    review = serializer.save(author=request.user)
                    profile.reviews.add(review)
                    _serializer = self.get_serializer(review)
                    return Response(_serializer.data, status=201)

                error_msg = get_serializer_error_message(serializer.errors)
                return Response({"message": error_msg}, status=400)

        except AssertionError as e:
            return Response({"message": str(e)}, status=403)

        except Exception as e:
            # TODO: log error
            return Response({"message": "Internal Server Error"}, status=403)

    def put(self, request, public_id, *args, **kwargs):

        try:
            review_public_id = request.data.get("public_id")
            if not review_public_id:
                return Response({"message": "Bad request params"}, status=400)

            assert request.user.public_id != public_id, "403 forbidden request!"
            with transaction.atomic():

                profile, profile_type = self.get_profile_and_profile_type(public_id)
                if not profile:
                    return Response({"message": "Profile does not exists"}, status=404)

                review = profile.reviews.get(id=review_public_id)
                serializer = ReviewWriteSerializer.merge_serialize(
                    instance, request.data
                )
                if serializer.is_valid():
                    _review = serializer.save()
                    _serializer = self.get_serializer(_review)
                    return Response(_serializer.data, status=200)

        except Review.DoesNotExist:
            return Response({"message": "Review not found"}, status=404)

        except AssertionError as e:
            return Response({"message": str(e)}, status=403)

        except Exception as e:
            # TODO: log error
            return Response({"message": "Internal Server Error"}, status=403)

    def delete(self, request, public_id, *args, **kwargs):
        try:
            review_public_id = request.query_params.get("rid")
            if not review_public_id:
                return Response({"message": "Bad request"}, status=400)

            assert request.user.public_id != public_id, "403 forbidden request!"
            with transaction.atomic():
                profile, profile_type = self.get_profile_and_profile_type(public_id)
                if not profile:
                    return Response({"message": "Profile does not exists"}, status=404)

                review = profile.reviews.get(id=review_public_id)
                review.delete()

                return Response({"message": "Review Deleted Successfully"}, status=204)

        except Review.DoesNotExist:
            return Response({"message": "Review not found"}, status=404)

        except AssertionError as e:
            return Response({"message": str(e)}, status=403)

        except Exception as e:
            # TODO: log error
            return Response({"message": "Internal Server Error"}, status=403)
