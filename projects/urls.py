from django.urls import path

from . import views

# e.g /apu/projects/*/**

urlpatterns = [
    # Projects
    path("", views.ProjectListAPIView.as_view(), name="project_list"),
    path(
        "<project_id>/", views.ProjectRetrieveAPIView.as_view(), name="project_retrieve"
    ),
    path(
        "<project_id>/update-status/",
        views.ProjectStatusUpdateAPIView.as_view(),
        name="project_status_update",
    ),
    # Milestones
    path(
        "milestones/create/",
        views.MilestoneCreateAPIView.as_view(),
        name="milestone_create",
    ),
    path(
        "milestones/update/",
        views.MilestoneUpdateAPIView.as_view(),
        name="milestone_update",
    ),
    path(
        "milestones/<project_id>/",
        views.MilestoneListAPIView.as_view(),
        name="milestone_list",
    ),
    # Acknowledgements
    path(
        "acknowledgements/create/",
        views.AcknowledgementCreateAPIView.as_view(),
        name="acknowledgement_create",
    ),
    path(
        "acknowledgements/update/",
        views.AcknowledgementUpdateAPIView.as_view(),
        name="acknowledgement_update",
    ),
    path(
        "acknowledgements/<project_id>/",
        views.AcknowledgementRetrieveAPIView.as_view(),
        name="acknowledgement_retrieve",
    ),
]
