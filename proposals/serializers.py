from rest_framework import serializers

from jobs.serializers import JobListSerializer
from talents.serializers import TalentReadSerializer

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
    job = serializers.SerializerMethodField()
    talent = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = [
            "public_id",
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
            "job", "talent"
        ]
        
    def get_job(self, instance:Proposal):
        return {
            "public_id": instance.job.public_id,
            "title": instance.job.title,
            "status": instance.job.status,
            "client":{
                "public_id": instance.job.client.public_id,
                "avatar": instance.job.client.logo,
                "name": instance.job.client.name,
                "rating": instance.job.client.rating,
            }
        }
        
    def get_talent(self, instance:Proposal):
        return {
            "public_id": instance.talent.public_id,
            "name": instance.talent.name,
            "title": instance.talent.title,
            "rating": instance.talent.rating,
            "badge": instance.talent.badge,
        }


class ProposalDetailSerializer(serializers.ModelSerializer):
    job = JobListSerializer()
    talent = TalentReadSerializer()
    attachments = AttachmentSerializer(many=True)

    class Meta:
        model = Proposal
        fields = [
            "public_id",
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
        readonly = True
        model = Proposal

        fields = [
            "public_id",
            "budget",
            "service_fee",
            "bits_amount",
            "attachments",
            "duration",
            "cover_letter",
            "job",
            "status",
            "created_at",
        ]

class ProposalReadSerializer(serializers.ModelSerializer):
    job = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(many=True)

    class Meta:
        readonly = True
        model = Proposal
        fields = [
            "public_id",
            "budget",
            "service_fee",
            "bits_amount",
            "attachments",
            "duration",
            "cover_letter",
            "job",
            "status",
            "created_at",
        ]

    def get_job(self, instance:Proposal):
        return {
            "public_id": instance.job.public_id,
            "title": instance.job.title,
            "status": instance.job.status,
        }


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
            "bits_amount",
            "duration",
            "cover_letter",
        ]


class ProposalPendingListSerializer(serializers.ModelSerializer):
    """
    This is a serializer for the list of pending proposals for the request user (talent)
    """

    talent = TalentReadSerializer()

    class Meta:
        model = Proposal
        fields = [
            "public_id",
            "budget",
            "service_fee",
            "talent",
            "duration",
            "created_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data.update({"job": get_job(instance)})
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
                "public_id": instance.job.client.public_id,
                "name": instance.job.client.name,
            }
            if instance.job.client
            else None
        ),
    }


def get_talent(instance: Proposal):
    return {
        "name": instance.talent.name,
        "public_id": instance.talent.public_id,
        "avatar": instance.talent.user.avatar,
        "rating": instance.talent.average_rating(),
    }
