from rest_framework import serializers

from jobs.models import Activities


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activities
        exclude = ["hired"]
