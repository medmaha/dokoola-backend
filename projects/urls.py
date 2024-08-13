from django.urls import path

from . import views

urlpatterns = [
    path("", views.ProjectListAPIView.as_view(), name="projects_list"),
    path("<project_id>/", views.ProjectRetrieveAPIView.as_view(), name="projects_list"),
]
