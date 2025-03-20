from rest_framework.serializers import ModelSerializer

from core.serializers import MergeSerializer

from .models import Review


class ReviewReadSerializer(ModelSerializer):

    class Meta:
        model = Review
        fields = [
            "id",
            "author",
            "text",
            "rating",
            "created_at",
        ]

    def to_representation(self, instance: Review):
        data = super().to_representation(instance)
        return {
            **data,
            "author": {
                "name": instance.author.name,
                "avatar": instance.author.avatar,
                "public_id": instance.author.public_id,
            },
        }


class ReviewWriteSerializer(MergeSerializer, ModelSerializer):

    class Meta:
        model = Review
        fields = [
            "text",
            "rating",
        ]
