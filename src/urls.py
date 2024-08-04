import os
from django.shortcuts import render
from django.contrib import admin
from django.core.mail import send_mail
from django.urls import path, re_path, include

from django.http import JsonResponse
from django.http import JsonResponse, HttpResponse


FRONTEND_URL = os.environ.get("FRONTEND_URL", "")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/jobs/", include("jobs.urls")),
    path("api/users/", include("users.urls")),
    path("api/staffs/", include("staffs.urls")),
    path("api/clients/", include("clients.urls")),
    path("api/reviews/", include("reviews.urls")),
    path("api/proposals/", include("proposals.urls")),
    path("api/contracts/", include("contracts.urls")),
    path("api/freelancers/", include("freelancers.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/messaging/", include("messaging.urls")),
    path("api/account/", include("users.account.urls")),
    path("", include("core.urls")),
    # re_path(r"api/$", base_api_index),
    # path("", base_index),
    # re_path(r".*", not_found),
]
