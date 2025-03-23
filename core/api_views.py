from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from core.models import Category, Feedback
from utilities.generator import get_serializer_error_message


# Categories ---------------------------------------------------------------------
class CategoryAPIView(GenericAPIView):
    permission_classes = []

    def get_queryset(self):
        categories = Category.objects.filter(disabled=False)
        return categories

    def get_serializer_class(self):
        class Serializer(serializers.ModelSerializer):
            class Meta:
                model = Category
                fields = ["slug", "name", "image_url", "description"]

        return Serializer

    def get(self, request):
        # ids = set()
        # slugs = set()
        # for _c in Category.objects.all():
        #     if _c.name not in slugs:
        #         ids.add(_c.id)
        #         slugs.add(_c.name)
        # Category.objects.exclude(id__in=ids).delete()

        categories = self.get_queryset()
        serializers = self.get_serializer(categories, many=True)
        categories = serializers.data

        response = Response(categories, status=200)
        return response


# Feedbacks ----=-----------------------------------------------------------------
class FeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["message", "author_name", "author_email", "rating"]


class FeedbackAPIView(GenericAPIView):
    permission_classes = []
    serializer_class = FeedbackCreateSerializer

    def get_serializer_class(self):
        class Serializer(serializers.ModelSerializer):
            class Meta:
                model = Feedback
                fields = [
                    "author_name",
                    "author_email",
                    "rating",
                    "likes_count",
                    "message",
                    "created_at",
                ]

        return Serializer

    def get(self, request):
        feedbacks = Feedback.objects.filter(blacklisted=False).order_by(
            "-rating", "-created_at"
        )[:3]

        serializers = self.get_serializer(feedbacks, many=True)
        feedbacks = serializers.data

        response = Response(feedbacks, status=200)
        return response

    def post(self, request):
        data = request.data.copy()

        early_return = False

        # If both author_name and author_email are not provided
        if (
            not data.get("author_name")
            and not data.get("author_email")
            and not data.get("rating")
        ):
            early_return = True

        # If message and rating are not provided
        if not data.get("message") and not data.get("rating"):
            early_return = True

        if early_return:
            return Response({"id": 10_0001}, status=200)

        feedback = self.get_serializer(data=data)
        if feedback.is_valid():
            instance = feedback.save()
            return Response({"id": instance.pk, "ok": True}, status=200)
        else:
            error_message = get_serializer_error_message(feedback.errors)
            return Response({"message": error_message}, status=400)
