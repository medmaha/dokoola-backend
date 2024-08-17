from rest_framework import serializers
from projects.models import Project

from .acknowledgement import AcknowledgementRetrieveSerializer
from .milestone import MilestoneRetrieveSerializer


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "duration", "deadline", "status", "created_at")

    def get_job(self, instance: Project):
        return {
            "slug": instance.contract.job.slug,
            "title": instance.contract.job.title,
        }

    def get_client(self, instance: Project):
        return {
            "name": instance.contract.client.user.name,
            "avatar": instance.contract.client.user.avatar,
            "username": instance.contract.client.user.username,
            "rating": instance.contract.client.user.calculate_rating(),
        }

    def get_freelancer(self, instance: Project):
        return {
            "name": instance.contract.freelancer.user.name,
            "avatar": instance.contract.freelancer.user.avatar,
            "username": instance.contract.freelancer.user.username,
            "rating": instance.contract.freelancer.user.calculate_rating(),
        }

    def to_representation(self, instance: Project):
        data = super().to_representation(instance)
        data["budget"] = instance.contract.proposal.budget

        data["contract_id"] = instance.contract.pk
        data["proposal_id"] = instance.contract.proposal.pk

        data["job"] = self.get_job(instance)
        data["client"] = self.get_client(instance)
        data["freelancer"] = self.get_freelancer(instance)
        return data


class ProjectRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "duration", "deadline", "status", "created_at")

    def get_job(self, instance: Project):
        return {
            "slug": instance.contract.job.slug,
            "title": instance.contract.job.title,
        }

    def get_client(self, instance: Project):
        return {
            "name": instance.contract.client.user.name,
            "avatar": instance.contract.client.user.avatar,
            "username": instance.contract.client.user.username,
            "rating": instance.contract.client.user.calculate_rating(),
        }

    def get_freelancer(self, instance: Project):
        return {
            "name": instance.contract.freelancer.user.name,
            "avatar": instance.contract.freelancer.user.avatar,
            "username": instance.contract.freelancer.user.username,
            "rating": instance.contract.freelancer.user.calculate_rating(),
        }

    def to_representation(self, instance: Project):
        data = super().to_representation(instance)
        data["budget"] = instance.contract.proposal.budget

        data["contract_id"] = instance.contract.pk
        data["proposal_id"] = instance.contract.proposal.pk

        data["job"] = self.get_job(instance)
        data["client"] = self.get_client(instance)
        data["freelancer"] = self.get_freelancer(instance)
        return data
