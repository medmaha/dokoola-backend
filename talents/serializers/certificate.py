from rest_framework import serializers

from core.serializers import MergeSerializer
from talents.models import Certificate


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
