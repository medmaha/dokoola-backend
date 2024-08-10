from django.urls import path

from . import views

urlpatterns = [
    path("", views.JobsListAPIView.as_view(), name="jobs_list"),
    path("create/", views.JobCreateAPIView.as_view(), name="job_create"),
    path("search/", views.JobsSearchAPIView.as_view(), name="job_searching"),
    path("update/", views.JobUpdateAPIView.as_view(), name="job_update"),
    path("<slug>/", views.JobDetailAPIView.as_view(), name="job_detail"),
    path("<slug>/activities/", views.JobActivitiesAPIView.as_view(), name="job_detail"),
]
