import os

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

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
    path("api/projects/", include("projects.urls")),
    path("api/talents/", include("talents.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/messaging/", include("messaging.urls")),
    path("api/account/", include("users.views.account.urls")),
    path("", include("core.urls")),
]


if settings.DEBUG:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )
    api_docs_urlpatterns = [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        # Optional UI:
        path(
            "api/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]

    urlpatterns.insert(0, path("silk/", include("silk.urls", namespace="silk")))
    urlpatterns += api_docs_urlpatterns
