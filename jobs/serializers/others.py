from rest_framework import serializers
from jobs.models import Pricing, Activities


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activities
        exclude = ["hired"]


class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        exclude = ["id"]
