from django.urls import path

from . import views, search

urlpatterns = [
    path("", views.FreelancerListAPIView.as_view(), name="freelancer_lists"),
    path("query", search.FreelancersSearchAPIView.as_view(), name="freelancer_search"),
    path(
        "<username>",
        views.FreelanceRetrieveAPIView.as_view(),
        name="freelancer_retrieve",
    ),
]
