from django.urls import path

from . import views


urlpatterns = [
    path("", views.ProposalListApiView.as_view(), name="proposals_list"),
    path("edit", views.ProposalUpdateAPIView.as_view(), name="proposals_edit"),
    path("create", views.ProposalCreateAPIView.as_view(), name="proposals_create"),
    path("check/<slug>", views.ProposalCheckAPIView.as_view(), name="proposals_check"),
]
