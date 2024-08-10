from rest_framework import serializers
from proposals.models import Proposal


class ContractRelatedDataSerializer(serializers.Serializer):

    class Meta:
        model = Proposal
        fields = []

    def to_representation(self, instance: Proposal):
        return get_related_fields(instance)


def get_related_fields(instance: Proposal):
    data = {}
    data["job"] = {
        "slug": instance.job.slug,
        "title": instance.job.title,
        "description": instance.job.description[:400],
        "location": instance.job.location,
        "budget": instance.job.budget,
        "payment_type": instance.job.payment_type,
        "duration": instance.duration,
    }
    data["proposal"] = {
        "id": instance.pk,
        "cover_letter": instance.cover_letter,
        "budget": instance.budget,
        "status": instance.status,
        "duration": instance.duration,
    }
    data["freelancer"] = {
        "id": instance.freelancer.pk,
        "name": instance.freelancer.user.get_full_name(),
        "username": instance.freelancer.user.username,
        "avatar": instance.freelancer.user.avatar,
        "rating": instance.freelancer.calculate_rating(),
    }

    data["client"] = {
        "id": instance.job.client.pk,
        "name": instance.job.client.user.get_full_name(),
        "username": instance.job.client.user.username,
        "avatar": instance.job.client.user.avatar,
        "rating": instance.job.client.calculate_rating(),
    }

    return data
