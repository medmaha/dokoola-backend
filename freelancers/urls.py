from django.urls import path

from . import views, search


# Url Pattern /api/freelancers/*/**

urlpatterns = [
    path("", views.FreelancerListAPIView.as_view(), name="freelancer_lists"),
    path("query", search.FreelancersSearchAPIView.as_view(), name="freelancer_search"),
    path(
        "<username>/",
        views.FreelanceRetrieveAPIView.as_view(),
        name="freelancer_retrieve",
    ),
    path(
        "<username>/projects/",
        views.FreelancerProjectsList.as_view(),
        name="freelancer_retrieve",
    ),
    path(
        "<username>/projects/pending",
        views.FreelancerProjectsList.as_view(),
        name="freelancer_retrieve",
    ),
    path(
        "<username>/update/",
        views.FreelancerUpdateAPIView.as_view(),
        name="freelancer_update",
    ),
    path(
        "<username>/mini-info/",
        views.FreelanceMiniInfoView.as_view(),
        name="freelancer_statistics",
    ),
]
