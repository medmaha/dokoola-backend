from rest_framework import serializers

from talents.models import Certificate

from .base import MergeSerializer


class TalentCertificateReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = [
            "public_id",
            "created_at",
            "updated_at",
            "name",
            "url",
            "organization",
            "published",
            "date_issued",
        ]


class TalentCertificateWriteSerializer(MergeSerializer, serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ["name", "url", "organization", "published", "date_issued"]
