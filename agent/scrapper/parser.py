import datetime
from abc import abstractmethod
from typing import Callable, List, Literal, Optional, final

from bs4 import BeautifulSoup

from .models import ScrapedJob
from .utils import clean_html_content, get_job_type_or_other, logger

ParserType = Literal["bs4", "lxml", "percel"]


class JobParser:
    def __init__(
        self,
        to_json=False,
        job_url: str = "",
        page_source: str = "",
        parsers: List[ParserType] = ["bs4"],
        callback: Optional[Callable[[ScrapedJob], None]] = None,
    ):
        self.callback = callback
        self.job_url = job_url

        self.bs4 = None
        self.lxml_tree = None

        self.bs4 = BeautifulSoup(page_source, "html.parser")
        # clean_html_content(self.bs4)

    @final
    def get_element_by_xpath(self, xpath):
        return None

    @abstractmethod
    def _get_title(self) -> str:
        """Extract job title"""
        pass

    @abstractmethod
    def _get_company_name(self) -> str:
        """Extract company name"""
        pass

    @abstractmethod
    def _get_description(self) -> str:
        """Extract job description"""
        pass

    @abstractmethod
    def _get_job_type(self) -> str:
        """Extract job type"""
        pass

    @abstractmethod
    def _get_location_info(self) -> str | None:
        """Extract location information"""
        pass

    @abstractmethod
    def _get_created_at(self) -> datetime.datetime | None:
        """Extract created at"""
        pass

    @abstractmethod
    def _get_application_deadline(self) -> datetime.datetime | None:
        """Extract application deadline"""
        pass

    @abstractmethod
    def _get_categories(self) -> List[str]:
        """Extract job categories"""
        pass

    @abstractmethod
    def _get_required_skills(self) -> List[str]:
        """Extract required skills"""
        pass

    @abstractmethod
    def _get_job_pricing(self) -> dict[str, str | int]:
        """Get the job pricing or an empty dic"""
        return dict()

    @abstractmethod
    def _get_job_benefits(self, job_description: Optional[str] = None) -> list:
        return []

    @abstractmethod
    def _get_site_name(self) -> str:
        return ""

    def clean_soup(
        self,
        soup=None,
        elements=None,
        classes=None,
        attrs=None,
    ):
        clean_html_content(
            soup or self.bs4, elems=elements, attrs=attrs, classes=classes
        )

    def sanitize_text(
        self,
        text: str,
        elements=None,
        classes=None,
        attrs=None,
    ):
        soup = BeautifulSoup(text, "html.parser")
        self.clean_soup(soup, elements, classes, attrs)
        return soup

    @final
    def parse(self) -> Optional[ScrapedJob]:
        """
        Parse job details from the page using Selenium
        Returns:
            Optional[ScrapedJob]: Parsed job object or None if parsing fails
        """

        try:
            title = self._get_title()
            if not title:
                print("[Error] no title")
                return None

            company_name = self._get_company_name()
            if not company_name:
                print("[Error] no company_name")
                return None

            description = self._get_description()
            if not description:
                print("[Error] no description")
                return None

            location_info = self._get_location_info()
            job_type = self._get_job_type()
            categories = self._get_categories()
            required_skills = self._get_required_skills()
            created_at = self._get_created_at()
            application_deadline = self._get_application_deadline()

            third_party_metadata = {
                "site_url": self.job_url,
                "site_name": self._get_site_name(),
                "categories": categories,
                "company_name": company_name,
            }

            job_type, job_type_other = get_job_type_or_other(job_type)

            job = ScrapedJob(
                url=self.job_url,
                title=title,
                job_type=job_type,
                created_at=created_at,
                description=description,
                country=location_info["country"],
                address=location_info["address"],
                application_deadline=application_deadline,
                third_party_metadata=third_party_metadata,
                required_skills=required_skills,
                pricing=self._get_job_pricing(),
                benefits=self._get_job_benefits(),
                job_type_other=job_type_other,
            )

            print(job)

            if self.callback:
                self.callback(job)

            return job
        except Exception as e:
            print(
                "[Error] [{}]".format(e),
            )
            raise
