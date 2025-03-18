from django.urls import path, re_path

from talents import views

from . import dashboard, search, views

# Url Pattern /api/talents/*/**

urlpatterns = [
    # Talent Dashboard APIView -----------------------------------
    # path(
    #     "dashboard/",
    #     views.TalentDashboardStatsView.as_view(),
    #     name="talent_dashboard",
    # ),
    path(
        "",
        views.TalentAPIView.as_view(),
        name="talent_route_noparam",
    ),
    path(
        "<public_id>/",
        views.TalentAPIView.as_view(),
        name="talent_route",
    ),
    path(
        "<public_id>/dashboard/",
        views.TalentDashboardAPIView.as_view(),
        name="talent_dashboard_route",
    ),
    path(
        "<public_id>/search/",
        views.TalentSearchAPIView.as_view(),
        name="talent_search_route",
    ),
    path(
        "<public_id>/portfolios/",
        views.TalentPortfolioAPIView.as_view(),
        name="talent_portfolio_route",
    ),
    path(
        "<public_id>/educations/",
        views.TalentEducationAPIView.as_view(),
        name="talent_education_route",
    ),
    path(
        "<public_id>/certificates/",
        views.TalentCertificateAPIView.as_view(),
        name="talent_certificate_route",
    ),
    # ----------------------------------------------------------------
    # Talent Projects APIView
    # path(
    #     "<public_id>/projects/",
    #     views.TalentProjectsList.as_view(),
    #     name="talent_retrieve",
    # ),
    # path(
    #     "<public_id>/projects/pending",
    #     views.TalentProjectsList.as_view(),
    #     name="talent_retrieve",
    # ),
    # ----------------------------------------------------------------
    #
]
