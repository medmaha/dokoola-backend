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
        "<public_id>/",
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
        "<public_id>/",
        views.ClientGenericAPIView.as_view(),
        name="client_details",
    ),
    path(
        "<public_id>/update/",
        views.ClientUpdateView.as_view(),
        name="client_update",
    ),
    path(
        "<public_id>/job-postings/",
        views.ClientJobPostingApiView.as_view(),
        name="client_job_postings",
    ),
]
