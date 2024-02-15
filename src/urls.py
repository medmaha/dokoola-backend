from django.contrib import admin

from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
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
]
