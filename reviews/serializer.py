

# create a review model serializer

from rest_framework.serializers import ModelSerializer

from users.serializer import UserSerializer

from .models import Review

class ReviewSerializer(ModelSerializer):
    author = UserSerializer()
    class Meta:
        model = Review
        fields = ['author', 'text', 'rating', 'updated_at',]
