from django.urls import path

from . import views

urlpatterns = [
    path("", views.JobListAPIView.as_view(), name="job_list"),
    path("me/", views.MyJobListAPIView.as_view(), name="my_job_list"),
    path("create/", views.JobCreateAPIView.as_view(), name="job_create"),
    path("search/", views.JobsSearchAPIView.as_view(), name="job_searching"),
    path("update/", views.JobUpdateAPIView.as_view(), name="job_update"),
    path("<job_id>/", views.JobRetrieveAPIView.as_view(), name="job_detail"),
    path("<slug>/activities/", views.JobActivitiesAPIView.as_view(), name="job_detail"),
]
