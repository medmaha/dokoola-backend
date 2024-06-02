from django.urls import path

from . import views


urlpatterns = [
    path("", views.ProposalListApiView.as_view(), name="proposals_list"),
    path("update/", views.ProposalUpdateAPIView.as_view(), name="proposals_edit"),
    path("create/", views.ProposalCreateAPIView.as_view(), name="proposals_create"),
    path("<pid>/", views.ProposalDetailsApiView.as_view(), name="proposals_list"),
    path(
        "<username>/pending/",
        views.ProposalPendingListView.as_view(),
        name="proposals_pending",
    ),
    path("check/<slug>/", views.ProposalCheckAPIView.as_view(), name="proposals_check"),
]
