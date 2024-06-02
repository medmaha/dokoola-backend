# create a review model serializer

from rest_framework.serializers import ModelSerializer

from users.serializer import UserSerializer

from .models import Review


class ReviewListSerializer(ModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Review
        fields = [
            "id",
            "author",
            "text",
            "rating",
            "created_at",
        ]


class ReviewCreateSerializer(ModelSerializer):

    class Meta:
        model = Review
        fields = [
            "text",
            "rating",
        ]
