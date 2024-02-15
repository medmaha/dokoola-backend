from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from users.models import User
from utilities.text import get_url_params

from .serializer import ReviewSerializer
from .models import Review


class ReviewsListView(ListAPIView):
    def get_queryset(self):
        user_id = get_url_params(self.request.get_full_path()).get('user_id')

        if user_id:
            try:
                user = User.objects.get(id=user_id)
                print(user)
                profile = user.profile # type: ignore
                try:
                    return profile.reviews.all()
                except Exception as e:
                    raise e
            except Exception as e:
                return []
        
        return []
    
    def list(self, request, *args, **kwargs):
        reviews = self.get_queryset()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=200)
