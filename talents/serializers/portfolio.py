from rest_framework import serializers

from talents.models import Portfolio

from .base import MergeSerializer


class TalentPortfolioReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = [
            "name",
            "description",
            "image",
            "published",
            "url",
            "public_id",
            "created_at",
            "updated_at",
        ]


class TalentPortfolioWriteSerializer(MergeSerializer, serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = [
            "name",
            "description",
            "image",
            "url",
            "published",
        ]
