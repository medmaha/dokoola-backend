from django.urls import path

from . import dashboard, search, views

# Url Pattern /api/talents/*/**

urlpatterns = [
    # Talent Dashboard APIView -----------------------------------
    path(
        "dashboard/",
        views.TalentDashboardStatsView.as_view(),
        name="talent_dashboard",
    ),
    path(
        "dashboard/query/",
        dashboard.TalentDashboardQuery.as_view(),
        name="talent_dashboard_query",
    ),
    # ----------------------------------------------------------------
    #
    # Talent Portfolio APIView -----------------------------------
    path(
        "portfolios/",
        views.TalentPortfolioAPIView.as_view(),
    ),
    path(
        "<username>/portfolios/",
        views.TalentPortfolioAPIView.as_view(),
    ),
    # ----------------------------------------------------------------
    #
    # Talent Certificate APIView
    path(
        "<username>/certificates/",
        views.TalentCertificateAPIView.as_view(),
    ),
    # ----------------------------------------------------------------
    #
    # Talent Education APIView
    path(
        "<username>/educations/",
        views.TalentEducationAPIView.as_view(),
    ),
    # ----------------------------------------------------------------
    # Talent Projects APIView
    path(
        "<username>/projects/",
        views.TalentProjectsList.as_view(),
        name="talent_retrieve",
    ),
    path(
        "<username>/projects/pending",
        views.TalentProjectsList.as_view(),
        name="talent_retrieve",
    ),
    # ----------------------------------------------------------------
    #
    path("", views.TalentListAPIView.as_view(), name="talent_lists"),
    path(
        "search/",
        search.TalentsSearchAPIView.as_view(),
        name="talent_search",
    ),
    path(
        "<public_id>/update/",
        views.TalentUpdateAPIView.as_view(),
        name="talent_update",
    ),
    path(
        "<username>/",
        views.TalentRetrieveAPIView.as_view(),
        name="talent_retrieve",
    ),
    path(
        "<username>/mini/",
        views.TalentMiniInfoView.as_view(),
        name="talent_statistics",
    ),
    #
]
