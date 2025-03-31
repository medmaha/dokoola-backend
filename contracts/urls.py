from django.urls import path

from . import views

# Url Pattern /api/contracts/*/**/

urlpatterns = [
    path(
        "",
        views.ContractAPIView.as_view(),  # method -> GET
        name="contracts",
    ),
    path(
        "create/",
        views.ContractCreateAPIView.as_view(),  # method -> POST
        name="contract_create",
    ),
    path(
        "<contract_id>/",
        views.ContractAPIView.as_view(),  # method -> GET/POST/PUT
        name="contracts",
    ),
    path(
        "<contract_id>/completed/",
        views.ContractCompleteAPIView.as_view(),  # method -> PUT
        name="contract_completed",
    ),
]
