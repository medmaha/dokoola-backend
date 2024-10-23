from django.urls import path

from . import dashboard, views

# Url Pattern /api/clients/*
urlpatterns = [
    path(
        "",
        views.ClientGenericAPIView.as_view(),
        name="client_generic_view",
    ),
    path(
        "<client_id>/",
        views.ClientGenericAPIView.as_view(),
        name="client_generic_view",
    ),
    path("info/", views.ClientJobDetailView.as_view(), name="client_info"),
    path(
        "dashboard/",
        dashboard.ClientDashboardAPIView.as_view(),
        name="client_stats",
    ),
    path(
        "<username>/",
        views.ClientGenericAPIView.as_view(),
        name="client_details",
    ),
    path(
        "<username>/update/",
        views.ClientUpdateView.as_view(),
        name="client_update",
    ),
    path(
        "<username>/job-postings/",
        views.ClientJobPostingApiView.as_view(),
        name="client_job_postings",
    ),
]
