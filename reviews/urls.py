from django.urls import path

from . import views

urlpatterns = [path("", views.ReviewsGenericAPIView.as_view(), name="reviews")]
