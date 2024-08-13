from django.db.models import F, Subquery
from rest_framework import serializers
from projects.models import Project, Acknowledgement


class AcknowledgementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acknowledgement
        fields = ("id", "comment", "acknowledged", "created_at")


class MilestoneSerializer(serializers.ModelSerializer):
    acknowledgement = AcknowledgementSerializer()

    class Meta:
        model = Project
        fields = (
            "id",
            "status",
            "milestone_name",
            "milestone_description",
            "acknowledgement",
            "created_at",
            "is_final",
        )


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

    def get_milestones(self, instance: Project):
        milestones = instance.milestones.all()
        return MilestoneSerializer(milestones, many=True, context=self.context).data

    def get_acknowledgement(self, instance: Project):
        if instance.acknowledgement is None:
            return None
        return AcknowledgementSerializer(
            instance.acknowledgement, context=self.context
        ).data

    def to_representation(self, instance: Project):
        data = super().to_representation(instance)
        data["budget"] = instance.contract.proposal.budget

        data["contract_id"] = instance.contract.id
        data["proposal_id"] = instance.contract.proposal.id

        data["job"] = self.get_job(instance)
        data["client"] = self.get_client(instance)
        data["freelancer"] = self.get_freelancer(instance)
        data["milestones"] = self.get_milestones(instance)
        data["acknowledgement"] = self.get_acknowledgement(instance)
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

    def get_milestones(self, instance: Project):
        milestones = instance.milestones.all()
        return MilestoneSerializer(milestones, many=True, context=self.context).data

    def get_acknowledgement(self, instance: Project):
        if instance.acknowledgement is None:
            return None
        return AcknowledgementSerializer(
            instance.acknowledgement, context=self.context
        ).data

    def to_representation(self, instance: Project):
        data = super().to_representation(instance)
        data["budget"] = instance.contract.proposal.budget

        data["contract_id"] = instance.contract.id
        data["proposal_id"] = instance.contract.proposal.id

        data["job"] = self.get_job(instance)
        data["client"] = self.get_client(instance)
        data["freelancer"] = self.get_freelancer(instance)
        data["milestones"] = self.get_milestones(instance)
        data["acknowledgement"] = self.get_acknowledgement(instance)
        return data
