from django.urls import path

from . import views, search

urlpatterns = [
    path("", views.JobsListAPIView.as_view(), name="jobs_list"),
    path("create", views.JobCreateAPIView.as_view(), name="job_create"),
    path("search", search.JobsSearchAPIView.as_view(), name="job_searching"),
    path("<slug>", views.JobDetailAPIView.as_view(), name="job_detail"),
]
