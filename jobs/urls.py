from django.urls import path

from . import views

urlpatterns = [
    path("", views.JobListAPIView.as_view(), name="job_list"),
    path("scraper/", views.JobScrapperAPIView.as_view(), name="job_scraper"),
    path("my-jobs/", views.MyJobListAPIView.as_view(), name="my_job_list"),
    path("create/", views.JobCreateAPIView.as_view(), name="job_create"),
    path("search/", views.JobsSearchAPIView.as_view(), name="job_searching"),
    path("sitemaps/", views.JobsSitemapAPIView.as_view(), name="job_sitemaps"),
    path("<public_id>/", views.JobRetrieveAPIView.as_view(), name="job_detail"),
    path("<public_id>/delete/", views.JobDeleteAPIView.as_view(), name="job_delete"),
    path(
        "<public_id>/third-party/",
        views.ThirdPartyJobAPIView.as_view(),
        name="job_third_party",
    ),
    path("<public_id>/edit/", views.JobUpdateAPIView.as_view(), name="job_update"),
    path("<public_id>/related/", views.JobRelatedAPIView.as_view(), name="job_related"),
    path(
        "<public_id>/activities/",
        views.JobActivitiesAPIView.as_view(),
        name="job_activities",
    ),
]
