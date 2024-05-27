import os
from django.contrib import admin
from django.urls import path, re_path, include

from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import JsonResponse
from django.middleware.csrf import get_token

from django.http import HttpResponseRedirect, JsonResponse, HttpResponse

DEFAULT_URL = "https://dokoola.vercel.app"
FRONTEND_URL = os.environ.get("FRONTEND_URL", DEFAULT_URL)


def index(request, *args, **kwargs):
    return HttpResponseRedirect(FRONTEND_URL)


def not_found(request):
    return HttpResponse("<h1>404 | Not Found!</h1>", status=404)


def api_index(request, *args, **kwargs):
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


@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({"csrf": get_token(request)})


def health(request):
    return JsonResponse({"status": "OK"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/csrf/", get_csrf_token, name="csrf_token"),
    path("api/jobs/", include("jobs.urls")),
    path("api/users/", include("users.urls")),
    path("api/staffs/", include("staffs.urls")),
    path("api/clients/", include("clients.urls")),
    path("api/reviews/", include("reviews.urls")),
    path("api/proposals/", include("proposals.urls")),
    path("api/freelancers/", include("freelancers.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/messenging/", include("messenging.urls")),
    path("api/account/", include("users.account.urls")),
    path("api/health/", health),
    re_path(r"^api/?(.*)?/?$", api_index),
    path("", index),
    re_path(r".*", not_found),
]
