from rest_framework import serializers

from core.serializers import MergeSerializer
from talents.models import Portfolio


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
