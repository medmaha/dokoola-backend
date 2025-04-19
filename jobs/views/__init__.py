from .delete import JobDeleteAPIView
from .get import (
    JobActivitiesAPIView,
    JobListAPIView,
    JobRelatedAPIView,
    JobRetrieveAPIView,
    MyJobListAPIView,
)
from .post import JobCreateAPIView
from .put import JobUpdateAPIView
from .scraper import JobScrapperAPIView
from .search import JobsSearchAPIView
from .sitemaps import JobsSitemapAPIView
from .third_party_job import ThirdPartyJobAPIView
