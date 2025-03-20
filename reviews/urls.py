from django.urls import path

from . import views

urlpatterns = [
    path("<str:public_id>/", views.ReviewsGenericAPIView.as_view(), name=""),
]
