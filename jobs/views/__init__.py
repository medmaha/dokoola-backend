from .delete import JobDeleteAPIView
from .get import (
    JobActivitiesAPIView,
    JobListAPIView,
    JobRetrieveAPIView,
    MyJobListAPIView,
    JobRelatedAPIView,
)
from .post import JobCreateAPIView
from .put import JobUpdateAPIView
from .search import JobsSearchAPIView
from .sitemaps import JobsSitemapAPIView
from .third_party_job import ThirdPartyJobAPIView