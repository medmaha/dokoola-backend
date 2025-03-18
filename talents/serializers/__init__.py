from .certificate import (
    TalentCertificateReadSerializer,
    TalentCertificateWriteSerializer,
)
from .education import TalentEducationReadSerializer, TalentEducationWriteSerializer
from .portfolio import TalentPortfolioReadSerializer, TalentPortfolioWriteSerializer
from .talent import TalentReadSerializer, TalentWriteSerializer

__all__ = (
    "TalentReadSerializer",
    "TalentWriteSerializer",
    "TalentPortfolioReadSerializer",
    "TalentPortfolioWriteSerializer",
    "TalentEducationReadSerializer",
    "TalentEducationWriteSerializer",
    "TalentCertificateReadSerializer",
    "TalentCertificateWriteSerializer",
)
