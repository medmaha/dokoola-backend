from django.urls import path

from . import views, dashboard


# Url Pattern /api/clients/*
urlpatterns = [
    path("", views.ClientListView.as_view(), name="client_list"),
    path("info/", views.ClientJobDetailView.as_view(), name="client_info"),
    path("dashboard/", dashboard.ClientDashboardAPIView.as_view(), name="client_stats"),
    path("<username>/", views.ClientListView.as_view(), name="client_details"),
    path("<username>/update/", views.ClientUpdateView.as_view(), name="client_update"),
]
