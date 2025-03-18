from datetime import datetime
from typing import Any

from rest_framework import serializers

from talents.models.education import Education

from .base import MergeSerializer


class TalentEducationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            "public_id",
            "created_at",
            "updated_at",
            "degree",
            "institution",
            "location",
            "start_date",
            "end_date",
            "achievements",
            "published",
        ]


class TalentEducationWriteSerializer(MergeSerializer, serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            "degree",
            "institution",
            "location",
            "start_date",
            "end_date",
            "achievements",
            "published",
        ]

    # def validate(self, data:dict[str, Any]):
    #     start_date = data.get('start_date')
    #     end_date = data.get('end_date')

    #     if not start_date:
    #         raise serializers.ValidationError({
    #             "start_date": "Start date is required",
    #         })

    #     if start_date > end_date:
    #         raise serializers.ValidationError({
    #             "start_date": "Start date cannot be later than end date"
    #         })

    #     if start_date > datetime.now().date():
    #         raise serializers.ValidationError({
    #             "start_date": "Start date cannot be in the future"
    #         })

    #     if end_date and end_date > datetime.now().date():
    #         raise serializers.ValidationError({
    #             "end_date": "End date cannot be in the future"
    #         })
    #     return data
