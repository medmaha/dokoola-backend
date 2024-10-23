from rest_framework import serializers

from jobs.serializers import JobListSerializer
from talents.serializers import (
    TalentMiniSerializer,
    TalentSerializer,
)

from .models import Attachment, Proposal


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = [
            "name",
            "file_url",
        ]


class ProposalListSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True)

    class Meta:
        model = Proposal
        fields = [
            "id",
            "budget",
            "service_fee",
            "bits_amount",
            "attachments",
            "cover_letter",
            "duration",
            "status",
            "is_reviewed",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data.update({"talent": get_talent(instance), "job": get_job(instance)})

        return data


class ProposalDetailSerializer(serializers.ModelSerializer):
    job = JobListSerializer()
    talent = TalentSerializer()
    attachments = AttachmentSerializer(many=True)

    class Meta:
        model = Proposal
        fields = [
            "id",
            "job",
            "budget",
            "service_fee",
            "talent",
            "bits_amount",
            "attachments",
            "cover_letter",
            "duration",
            "status",
            "is_reviewed",
            "created_at",
            "updated_at",
        ]


class ProposalUpdateSerializer(serializers.ModelSerializer):
    job = JobListSerializer()
    attachments = AttachmentSerializer(many=True)

    class Meta:
        model = Proposal
        fields = [
            "id",
            "budget",
            "service_fee",
            "bits_amount",
            "attachments",
            "duration",
            "cover_letter",
            "job",
            "created_at",
        ]


class ProposalEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = [
            "cover_letter",
            "bits_amount",
            "budget",
            "duration",
        ]


class ProposalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = [
            "budget",
            "service_fee",
            "bits_amount",
            "duration",
            "cover_letter",
        ]


class ProposalPendingListSerializer(serializers.ModelSerializer):
    """
    This is a serializer for the list of pending proposals for the request user (talent)
    """

    class Meta:
        model = Proposal
        fields = [
            "id",
            "budget",
            "service_fee",
            "talent",
            "duration",
            "created_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data.update({"job": get_job(instance)})
        data.update({"talent": get_talent(instance)})
        data["cover_letter"] = instance.cover_letter[:150]

        return data


def get_job(instance: Proposal):
    return {
        "slug": instance.job.id,
        "title": instance.job.title,
        "description": instance.job.description[:100],
        "status": instance.job.status,
        "client": (
            {
                "avatar": instance.job.client.user.avatar,
                "username": instance.job.client.user.username,
                "name": instance.job.client.user.name,
            }
            if instance.job.client
            else None
        ),
    }


def get_talent(instance: Proposal):
    return {
        "name": instance.talent.user.name,
        "username": instance.talent.user.username,
        "avatar": instance.talent.user.avatar,
        "rating": instance.talent.user.calculate_rating(),
    }
