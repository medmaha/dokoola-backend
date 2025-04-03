import datetime
from typing import Callable, Optional

from bs4 import BeautifulSoup
from django.utils import timezone

from agent.scrapper.base import JobParser, JobScraper, ScrapedJob
from agent.scrapper.utils import clean_html_content
from utilities.time import utc_datetime


class GamJobParser(JobParser):

    def __init__(
        self,
        job_url: Optional[str] = "",
        page_source: Optional[str] = None,
        callback: Callable[[ScrapedJob], None] = None,
    ):
        super().__init__(
            parsers=["bs4"],
            job_url=job_url,
            callback=callback,
            page_source=page_source,
        )

    def _get_title(self):
        title_elm = self.bs4.find("h1", class_="page-title")
        if title_elm:
            return (
                list(title_elm.children)[0]
                .text.strip()
                .replace("(Re-advertised)", "")
                .replace("(Re-Advertised)", "")
            )
        return None

    def _get_company_name(self):
        company_name_elm = self.bs4.find("h3", class_="company-title")
        if company_name_elm:
            return company_name_elm.text.strip()
        return None

    def _get_description(self):
        soup = BeautifulSoup(str(self.bs4), "html.parser")
        clean_html_content(soup, elems=["a"])
        description = soup.find("div", attrs={"itemprop": "description"})
        if not description:
            return None

        description = description.prettify()
        if isinstance(description, bytes):
            description = description.decode(self.soup.original_encoding)
        return description

    def _get_job_type(self):
        job_type_elem = self.bs4.find("span", class_="job-type")
        return job_type_elem.text.strip() if job_type_elem else "N/A"

    def _get_location_info(self):
        locations = []
        country = {}
        address = ""

        locations_elm = self.bs4.find("span", class_="job-location")
        if locations_elm:
            for anchor in locations_elm.find_all("a"):
                _v = anchor.text.strip()
                if _v:
                    locations.append(_v)

            address = " - ".join(locations[:-1])
            country = {"name": locations[-1]} if locations else {}

        return {"country": country, "address": address}

    def _get_created_at(self):
        date_elem = self.bs4.find("span", class_="job-date__posted")

        if not date_elem:
            return None

        # Sample "- March 14, 2025"
        _date = str(date_elem.text.strip()).replace("- ", "")
        return self.__get_utc_date(timezone.datetime.strptime(_date, "%B %d, %Y"))

    def _get_application_deadline(self):
        date_elem = self.bs4.find("span", class_="job-date__closing")

        if not date_elem:
            return None

        # Sample "- March 14, 2025"
        _date = str(date_elem.text.strip()).replace("- ", "")
        return self.__get_utc_date(timezone.datetime.strptime(_date, "%B %d, %Y"))

    def _get_required_skills(self):
        categories = []
        categories_elm = self.bs4.select("span.job-category a")
        if categories_elm:
            for anchor in categories_elm:
                _v = anchor.text.strip()
                if _v:
                    categories.append(_v)
        return categories

    def _get_categories(self):
        categories = []
        # categories_elm = self.bs4.select("span.job-category a")
        # if categories_elm:
        #     for anchor in categories_elm:
        #         _v = anchor.text.strip()
        #         if _v:
        #             categories.append(_v)
        return categories

    def __get_utc_date(self, date: datetime.datetime):
        return utc_datetime(date.timestamp(), add_minutes=0)


class GamJobScraper(JobScraper):

    _BASE_URL = "https://gamjobs.com"

    def __init__(
        self,
        to_json=False,
        base_url: str = _BASE_URL,
        max_jobs: Optional[int] = None,
    ):
        super().__init__(
            to_json=to_json,
            pathname="/jobs",
            base_url=base_url,
            max_jobs=max_jobs,
            parser=GamJobParser,
            job_link_selectors=".job-details-link",
        )

    def scrape(self):
        """
        Scrape all jobs from the website
        Returns:
            List[GamJob]: List of parsed job objects
        """

        super().scrape()
        self._update_metadata()
        return self.jobs

    def on_settled(self):
        self._write_jobs_in_file()

    def _update_metadata(self) -> None:
        max_length = 300
        qualified_sentence_length = 50

        for job in self.jobs:
            description = []
            seen_content = set()
            relevant_tags = ["p", "div"]

            soup = BeautifulSoup(job.description, "html.parser")

            content_containers = soup.find_all(
                lambda tag: tag.name in relevant_tags
                and len(tag.get_text(strip=True)) > qualified_sentence_length
            )

            for container in content_containers:
                text = container.get_text(strip=True)

                if text in seen_content or len(text) < qualified_sentence_length:
                    continue

                seen_content.add(text)
                description.append(text)

                if sum(len(line) for line in description) > max_length:
                    break

            job.third_party_metadata.update(
                {
                    "source": "gamjobs.com",
                    "short_description": " ".join(description)[:max_length],
                }
            )
