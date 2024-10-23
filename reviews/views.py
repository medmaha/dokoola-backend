from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from users.models import User

from .models import Review
from .serializer import ReviewCreateSerializer, ReviewListSerializer


class ReviewsGenericAPIView(GenericAPIView):

    def get_profile(self):
        username = self.request.query_params.get("user")  # type: ignore
        try:
            user = User.objects.get(username=username)
            profile, _ = user.profile
            return profile
        except User.DoesNotExist:
            return None
        except Exception:
            pass

    def get_queryset(self):
        profile = self.get_profile()
        if not profile:
            return None
        return profile.reviews.all().order_by("-created_at")

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset is None:
            return Response({"message": "This request is prohibited"}, status=403)
        page = self.paginate_queryset(queryset)
        serializer = ReviewListSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        profile = self.get_profile()
        if not profile:
            return Response({"message": "This request is prohibited"}, status=403)

        serializer = ReviewCreateSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(author=request.user)
            profile.reviews.add(review)
            return Response(serializer.data, status=200)

        return Response({"message": str(serializer.errors)}, status=400)

    def put(self, request, *args, **kwargs):
        review_id = request.query_params.get("rid")

        with transaction.atomic():
            if not review_id:
                return Response({"message": "Bad request"}, status=400)
            try:
                review = Review.objects.select_for_update().get(
                    id=review_id, author=request.user
                )
            except Review.DoesNotExist:
                return Response({"message": "Review not found"}, status=404)

            serializer = ReviewCreateSerializer(instance=review, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Review updated"}, status=200)

    def delete(self, request, *args, **kwargs):
        review_id = request.query_params.get("rid")
        if not review_id:
            return Response({"message": "Bad request"}, status=400)
        try:
            with transaction.atomic():
                profile, _ = request.user.profile
                review = Review.objects.select_for_update().get(
                    id=review_id, author=request.user
                )
                profile.reviews.remove(review)
                review.delete()
                return Response({"message": "Review Deleted Successfully"}, status=200)
        except Review.DoesNotExist:
            return Response({"message": "Review not found"}, status=404)

        except Exception:

            return Response({"message": "Review not found"}, status=404)
