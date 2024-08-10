from . import views
from django.urls import path


# Url Pattern /api/contracts/*/**/

urlpatterns = [
    path("", views.ContractListAPIView.as_view(), name="contracts"),
    path("create/", views.ContractCreateAPIView.as_view(), name="contract-create"),
    path(
        "accept/<contract_id>/",
        views.ContractAcceptAPIView.as_view(),
        name="contract-accept",
    ),
    path(
        "reject/<contract_id>/",
        views.ContractAcceptAPIView.as_view(),
        name="contract-reject",
    ),
    path(
        "completed/<contract_id>/",
        views.ContractCompleteAPIView.as_view(),
        name="contract-completed",
    ),
    path(
        "<contract_id>/",
        views.ContractRetrieveAPIView.as_view(),
        name="contract_retrieve",
    ),
]
