from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup
from django.utils import timezone

from agent.scrapper.base import JobParser, JobScraper, ScrapedJob


class GamJobParser(JobParser):
    def __init__(
        self,
        url: Optional[str] = "",
        html_content: Optional[str] = None,
        soup: Optional[BeautifulSoup] = None,
    ):
        super().__init__(url=url, html_content=html_content, soup=soup)

    def _get_title(self):
        title_elm = self.job_detail.find("h1", class_="page-title")
        if title_elm:
            return list(title_elm.children)[0].text.strip()
        return None

    def _get_company_name(self):
        company_name_elm = self.job_company.find("h3", class_="company-title")
        if company_name_elm:
            return company_name_elm.text.strip()
        return None

    def _get_description(self):
        description = self.job_detail.find("div", attrs={"itemprop": "description"})
        if not description:
            return None

        description = description.prettify()
        if isinstance(description, bytes):
            description = description.decode(self.soup.original_encoding)
        return description

    def _get_job_type(self):
        job_type_elem = self.job_detail.find("span", class_="job-type")
        return job_type_elem.text.strip() if job_type_elem else "N/A"

    def _get_job_type_other(self, job_type: str):

        if "full" in job_type:
            return ["full-time", None]
        elif "part" in job_type:
            return ["part-time", None]
        elif "freelance" in job_type:
            return ["freelance", None]
        elif "contract" in job_type:
            return ["contract", None]
        elif "intern" in job_type:
            return ["internship", None]
        else:
            return ["other", job_type]

    def _get_location_info(self):
        locations = []
        country = {}
        address = ""

        locations_elm = self.job_detail.find("span", class_="job-location")
        if locations_elm:
            for anchor in locations_elm.find_all("a"):
                _v = anchor.text.strip()
                if _v:
                    locations.append(_v)

            address = " - ".join(locations[:-1])
            country = {"name": locations[-1]} if locations else {}

        return {"country": country, "address": address}

    def _get_created_at(self):
        date_elem = self.job_detail.find("span", class_="job-date__posted")

        if not date_elem:
            return None

        # Sample "- March 14, 2025"
        _date = str(date_elem.text.strip()).replace("- ", "")
        return timezone.datetime.strptime(_date, "%B %d, %Y")

    def _get_application_deadline(self):
        date_elem = self.job_detail.find("span", class_="job-date__closing")

        if not date_elem:
            return None

        # Sample "- March 14, 2025"
        _date = str(date_elem.text.strip()).replace("- ", "")
        return datetime.strptime(_date, "%B %d, %Y")

    def _required_skills(self):
        categories = []
        categories_elm = self.job_detail.select("span.job-category a")
        if categories_elm:
            for anchor in categories_elm:
                _v = anchor.text.strip()
                if _v:
                    categories.append(_v)
        return categories

    def _get_categories(self):
        categories = []
        # categories_elm = self.job_detail.select("span.job-category a")
        # if categories_elm:
        #     for anchor in categories_elm:
        #         _v = anchor.text.strip()
        #         if _v:
        #             categories.append(_v)
        return categories


class GamJobScraper(JobScraper):
    """
    A scraper for gamjobs.com that extracts job listings.

    This scraper inherits from the base JobScraper class and implements
    scraping functionality specific to gamjobs.com. It handles pagination,
    rate limiting, and parsing of job details from the site's HTML structure.

    The scraper uses a ThreadPoolExecutor for concurrent requests while
    respecting rate limits. It extracts job information like:
    - Title
    - Company
    - Description
    - Location
    - Job type
    - Required skills
    - Posting date
    - Application deadline

    Usage:
        scraper = GamJobScraper()
        jobs = scraper.scrape()
    """

    _BASE_URL = "https://gamjobs.com"

    def __init__(self, max_workers: int = 3, base_url: str = _BASE_URL, to_json=False):
        super().__init__(
            max_workers=max_workers,
            base_url=base_url,
            to_json=to_json,
            parser=GamJobParser,
        )

    def scrape(self):
        """
        Scrape all jobs from the website
        Returns:
            List[GamJob]: List of parsed job objects
        """
        jobs = super().scrape(pathname="/jobs", link_class="job-details-link")
        self.update_metadata(jobs)
        return jobs

    def update_metadata(self, jobs: List[ScrapedJob]):

        for job in jobs:

            job.third_party_metadata.update(
                {
                    "source": "gamjobs.com",
                    "source_url": job.url,
                }
            )

            soup = BeautifulSoup(job.description, "html.parser")

            description = ""
            relevant_tags = ["p", "li", "div", "span"]
            content_containers = soup.find_all(
                lambda tag: tag.name in relevant_tags
                and len(tag.get_text(strip=True)) > 30
            )

            seen_content = set()
            for container in content_containers:
                text = container.get_text(strip=True)

                if text in seen_content or len(text) < 30:
                    continue

                seen_content.add(text)

                description += text + "\n\n"

                if len(description) > 1000:
                    break

            description = description.strip()

            job.third_party_metadata["description"] = description

        return jobs
