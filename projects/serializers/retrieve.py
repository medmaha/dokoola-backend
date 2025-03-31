from rest_framework import serializers

from projects.models import Project

from .acknowledgement import AcknowledgementRetrieveSerializer
from .milestone import MilestoneRetrieveSerializer


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("public_id", "duration", "deadline", "status", "created_at")

    def get_job(self, instance: Project):
        return {
            "title": instance.contract.job.title,
            "public_id": instance.contract.job.public_id,
        }

    def get_client(self, instance: Project):
        return {
            "name": instance.contract.client.name,
            "avatar": instance.contract.client.user.avatar,
            "public_id": instance.contract.client.public_id,
            "rating": instance.contract.client.average_rating(),
        }

    def get_talent(self, instance: Project):
        return {
            "name": instance.contract.talent.name,
            "avatar": instance.contract.talent.user.avatar,
            "public_id": instance.contract.talent.public_id,
            "rating": instance.contract.talent.average_rating(),
        }

    def to_representation(self, instance: Project):
        data = super().to_representation(instance)
        data["budget"] = instance.contract.proposal.budget

        data["contract_id"] = instance.contract.public_id
        data["proposal_id"] = instance.contract.proposal.public_id

        data["job"] = self.get_job(instance)
        data["client"] = self.get_client(instance)
        data["talent"] = self.get_talent(instance)
        return data


class ProjectRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("public_id", "duration", "deadline", "status", "created_at")

    def get_job(self, instance: Project):
        return {
            "public_id": instance.contract.job.public_id,
            "title": instance.contract.job.title,
        }

    def get_client(self, instance: Project):
        return {
            "name": instance.contract.client.user.name,
            "avatar": instance.contract.client.user.avatar,
            "public_id": instance.contract.client.user.public_id,
            "rating": instance.contract.client.average_rating(),
        }

    def get_talent(self, instance: Project):
        return {
            "name": instance.contract.talent.user.name,
            "avatar": instance.contract.talent.user.avatar,
            "public_id": instance.contract.talent.user.public_id,
            "rating": instance.contract.talent.average_rating(),
        }

    def to_representation(self, instance: Project):
        data = super().to_representation(instance)
        data["budget"] = instance.contract.proposal.budget

        data["contract_id"] = instance.contract.pk
        data["proposal_id"] = instance.contract.proposal.pk

        data["job"] = self.get_job(instance)
        data["client"] = self.get_client(instance)
        data["talent"] = self.get_talent(instance)
        return data
