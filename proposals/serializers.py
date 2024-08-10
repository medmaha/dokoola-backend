from rest_framework import serializers

from freelancers.serializers import FreelancerSerializer, FreelancerMiniSerializer
from jobs.serializers import JobListSerializer, JobMiniSerializer

from .models import Proposal, Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = [
            "name",
            "file_url",
        ]


class ProposalListSerializer(serializers.ModelSerializer):
    job = JobMiniSerializer()
    freelancer = FreelancerMiniSerializer()
    attachments = AttachmentSerializer(many=True)

    class Meta:
        model = Proposal
        fields = [
            "id",
            "job",
            "budget",
            "service_fee",
            "freelancer",
            "bits_amount",
            "attachments",
            "cover_letter",
            "is_decline",
            "is_accepted",
            "duration",
            "status",
            "is_reviewed",
            "is_proposed",
            "created_at",
        ]


class ProposalDetailSerializer(serializers.ModelSerializer):
    job = JobListSerializer()
    freelancer = FreelancerSerializer()
    attachments = AttachmentSerializer(many=True)

    class Meta:
        model = Proposal
        fields = [
            "id",
            "job",
            "budget",
            "service_fee",
            "freelancer",
            "bits_amount",
            "attachments",
            "cover_letter",
            "is_decline",
            "duration",
            "status",
            "is_accepted",
            "is_reviewed",
            "is_proposed",
            "created_at",
        ]


class ProposalUpdateSerializer(serializers.ModelSerializer):
    job = JobMiniSerializer()
    attachments = AttachmentSerializer(many=True)

    class Meta:
        model = Proposal
        fields = [
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
    This is a serializer for the list of pending proposals for the request user (freelancer)
    """

    def get_job(self, obj: Proposal):
        return {
            "slug": obj.job.slug,
            "title": obj.job.title,
            "description": obj.job.description[:100],
            "client": {
                "avatar": obj.job.client.user.avatar,
                "username": obj.job.client.user.username,
                "name": obj.job.client.user.name,
            },
        }

    class Meta:
        model = Proposal
        fields = [
            "id",
            "budget",
            "service_fee",
            "freelancer",
            "duration",
            "created_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update({"job": self.get_job(instance)})
        data["cover_letter"] = instance.cover_letter[:150]

        return data
