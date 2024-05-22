from rest_framework import serializers

from freelancers.serializers import FreelancerSerializer, FreelancerMiniSerializer
from jobs.serializer import JobsSerializer, JobMiniSerializer

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
            "is_reviewed",
            "is_proposed",
            "created_at",
        ]


class ProposalDetailSerializer(serializers.ModelSerializer):
    job = JobsSerializer()
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
            "cover_letter",
            "job",
            "created_at",
        ]


class ProposalEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = ["cover_letter", "bits_amount", "budget"]


class ProposalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = [
            "budget",
            "service_fee",
            "bits_amount",
            "cover_letter",
        ]
