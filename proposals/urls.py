from django.urls import path

from . import views

urlpatterns = [
    path("", views.ProposalListApiView.as_view(), name="proposals_list"),
    path(
        "<publid_id>/edit/",
        views.ProposalUpdateAPIView.as_view(),
        name="proposals_edit",
    ),
    path(
        "create/",
        views.ProposalCreateAPIView.as_view(),
        name="proposals_create",
    ),
    path(
        "<publid_id>/",
        views.ProposalRetrieveApiView.as_view(),
        name="proposals_list",
    ),
    path(
        "<public_id>/pending/",
        views.ProposalPendingListView.as_view(),
        name="proposals_pending",
    ),
    path(
        "check/<slug>/",
        views.ProposalCheckAPIView.as_view(),
        name="proposals_check",
    ),
]
