import os
from django.shortcuts import render
from django.contrib import admin
from django.core.mail import send_mail
from django.urls import path, re_path, include

from django.http import JsonResponse
from django.http import JsonResponse, HttpResponse


FRONTEND_URL = os.environ.get("FRONTEND_URL", "")


def base_index(request, *args, **kwargs):
    return render(request, "core/index.html")


def base_api_index(request, *args, **kwargs):
    try:
        endpoint = args[0]
        if not endpoint:
            raise Exception("Endpoint not found")
        return JsonResponse(
            {
                "Provider": "Dokoola",
                "message": "Oops! API endpoint not found",
            },
            status=404,
        )
    except:
        return JsonResponse(
            {
                "message": "Welcome to Dokoola API",
            }
        )


def api_health(request):
    return JsonResponse({"status": "OK"})


def not_found(request):
    return HttpResponse("<h1>404 | Not Found!</h1>", status=404)


def mailer_health(request):
    response = send_mail(
        "Dokoola - Email Testing",
        f"""
            This is a test
        """,
        None,
        ["toure925@outlook.com"],
        fail_silently=False,
    )
    return JsonResponse({"status": "Ok" if bool(response) else "Failed"})


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
    path("api/messenging/", include("messenging.urls")),
    path("api/account/", include("users.account.urls")),
    path("api/health", api_health),
    path("api/health/", api_health),
    path("api/health/mail", mailer_health),
    path("api/health/mail/", mailer_health),
    path("", include("core.urls")),
    # re_path(r"api/$", base_api_index),
    # path("", base_index),
    # re_path(r".*", not_found),
]
