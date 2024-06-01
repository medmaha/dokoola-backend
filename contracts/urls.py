from . import views
from django.urls import path

urlpatterns = [
    path("", views.ContractListAPIView.as_view(), name="contracts"),
    path("create/", views.ContractCreateView.as_view(), name="contract-create"),
    path(
        "accept/<contract_id>/",
        views.ContractAcceptAPIView.as_view(),
        name="contract-accept",
    ),
    path(
        "<contract_id>/",
        views.ContractRetrieveAPIView.as_view(),
        name="contract_retrieve",
    ),
]
