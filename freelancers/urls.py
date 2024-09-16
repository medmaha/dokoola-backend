from django.urls import path

from . import views, search, dashboard

# Url Pattern /api/freelancers/*/**

urlpatterns = [
    # Freelancer Dashboard APIView -----------------------------------
    path(
        "dashboard/",
        views.FreelancerDashboardStatsView.as_view(),
        name="freelancer_dashboard",
    ),
    path(
        "dashboard/query/",
        dashboard.FreelancerDashboardQuery.as_view(),
        name="freelancer_dashboard_query",
    ),
    # ----------------------------------------------------------------
    #
    # Freelancer Portfolio APIView -----------------------------------
    path(
        "portfolios/",
        views.FreelancerPortfolioAPIView.as_view(),
    ),
    path(
        "<username>/portfolios/",
        views.FreelancerPortfolioAPIView.as_view(),
    ),
    # ----------------------------------------------------------------
    #
    # Freelancer Certificate APIView
    path(
        "<username>/certificates/",
        views.FreelancerCertificateAPIView.as_view(),
    ),
    # ----------------------------------------------------------------
    #
    # Freelancer Education APIView
    path(
        "<username>/educations/",
        views.FreelancerEducationAPIView.as_view(),
    ),
    # ----------------------------------------------------------------
    #
    # Freelancer Projects APIView
    path(
        "<username>/projects/",
        views.FreelancerProjectsList.as_view(),
        name="freelancer_retrieve",
    ),
    path(
        "<username>/projects/pending",
        views.FreelancerProjectsList.as_view(),
        name="freelancer_retrieve",
    ),
    # ----------------------------------------------------------------
    #
    path("", views.FreelancerListAPIView.as_view(), name="freelancer_lists"),
    path(
        "search/", search.FreelancersSearchAPIView.as_view(), name="freelancer_search"
    ),
    path(
        "<username>/update/",
        views.FreelancerUpdateAPIView.as_view(),
        name="freelancer_update",
    ),
    path(
        "<username>/",
        views.FreelanceRetrieveAPIView.as_view(),
        name="freelancer_retrieve",
    ),
    path(
        "<username>/mini-info/",
        views.FreelanceMiniInfoView.as_view(),
        name="freelancer_statistics",
    ),
    #
]
