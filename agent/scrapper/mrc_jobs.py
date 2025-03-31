from datetime import datetime
from typing import Callable, Dict, List, Optional

from bs4 import BeautifulSoup

from .base import JobParser, JobScraper
from .models import ScrapedJob


class MRCJobParser(JobParser):

    def __init__(
        self,
        job_url: Optional[str] = "",
        page_source: Optional[str] = None,
        callback: Callable[[ScrapedJob], None] = None,
    ):
        super().__init__(
            job_url=job_url, callback=callback, page_source=page_source, parsers=["bs4"]
        )

    def _get_title(self):
        title = self.bs4.find("h1", class_="job-title")
        return title.get_text(strip=True) if title else None

    def _get_company_name(self) -> str:
        company = self.bs4.find("div", class_="company-name")
        return company.get_text(strip=True) if company else "MRC Gambia"

    def _get_description(self) -> str:
        desc = self.bs4.find("div", class_="job-description")
        return desc.get_text(separator="\n").strip() if desc else None

    def _get_job_type(self) -> str:
        job_type = self.bs4.find("span", class_="employment-type")
        return job_type.get_text(strip=True) if job_type else "Full-time"

    def _get_location_info(self) -> dict:
        location = self.bs4.find("div", class_="job-location")
        return {
            "address": location.get_text(strip=True) if location else "Banjul, Gambia",
            "country": {"name": "Gambia", "code": "GM"},
        }

    def _get_created_at(self) -> Optional[datetime]:
        date_str = self.bs4.find("span", class_="post-date")
        return datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.now()

    def _get_application_deadline(self) -> Optional[datetime]:
        deadline = self.bs4.find("span", class_="application-deadline")
        return (
            datetime.strptime(deadline.get_text(strip=True), "%Y-%m-%d")
            if deadline
            else None
        )

    def _get_categories(self) -> List[str]:
        categories = self.bs4.select("div.job-categories span")
        return [cat.get_text(strip=True) for cat in categories]

    def _required_skills(self) -> List[str]:
        skills = self.bs4.select("ul.skills-list li")
        return [skill.get_text(strip=True) for skill in skills]

    def _get_job_benefits(self, job_description: Optional[str] = None) -> list:
        benefits = self.bs4.select("div.benefits li")
        return [benefit.get_text(strip=True) for benefit in benefits]

    def _get_site_name(self) -> str:
        return "MRC Gambia Recruitment Portal"


class MRCJobScraper(JobScraper):
    def __init__(self, max_jobs: Optional[int] = 20, to_json=None):
        super().__init__(
            parser=MRCJobParser,
            to_json=to_json,
            pathname="/recruitment/job-openings",
            job_link_selectors="div.job-listing a.job-link",
            max_jobs=max_jobs,
            base_url="https://apps.mrc.gm",
        )
