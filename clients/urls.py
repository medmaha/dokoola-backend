from django.urls import path

from . import views


# Url Pattern /api/clients/*
urlpatterns = [
    path("", views.ClientListView.as_view(), name="clients"),
    path("info/", views.ClientJobDetailView.as_view(), name="clients"),
    path("<pk>", views.ClientListView.as_view(), name="client_retrieve1"),
    path("<username>", views.ClientListView.as_view(), name="client_retrieve"),
    path("<username>/update/", views.ClientUpdateView.as_view(), name="client_update"),
]
