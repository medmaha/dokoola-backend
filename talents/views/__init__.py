from .application_ids import TalentApplicationIdsAPIView
from .certificates import TalentCertificateAPIView
from .dashboard import TalentDashboardAPIView
from .education import TalentEducationAPIView
from .portfolio import TalentPortfolioAPIView
from .search import TalentSearchAPIView
from .talent import TalentAPIView

__all__ = [
    "TalentAPIView",
    "TalentSearchAPIView",
    "TalentDashboardAPIView",
    "TalentPortfolioAPIView",
    "TalentEducationAPIView",
    "TalentCertificateAPIView",
    "TalentApplicationIdsAPIView",
]
