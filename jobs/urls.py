from django.urls import path

from . import views

urlpatterns = [
    path("", views.JobListAPIView.as_view(), name="job_list"),
    path("me/", views.MyJobListAPIView.as_view(), name="my_job_list"),
    path("create/", views.JobCreateAPIView.as_view(), name="job_create"),
    path("search/", views.JobsSearchAPIView.as_view(), name="job_searching"),
    path("<public_id>/", views.JobRetrieveAPIView.as_view(), name="job_detail"),
    path("<public_id>/edit/", views.JobUpdateAPIView.as_view(), name="job_update"),
    path(
        "<public_id>/activities/",
        views.JobActivitiesAPIView.as_view(),
        name="job_activities",
    ),
]
