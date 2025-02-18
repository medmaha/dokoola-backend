from concurrent.futures import ThreadPoolExecutor
import datetime
import threading

import requests
from typing import List
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class GamJob:
    title: str
    description: str
    address: str
    job_type: str
    pricing: dict
    country: dict
    benefits: dict
    created_at: datetime
    application_deadline: datetime
    required_skills: List[str]
    third_party_metadata: dict


class GamJobParser:
    def __init__(self, html_content=None, soup=None):
        if html_content:
            self.soup = BeautifulSoup(html_content, "html.parser")
        elif soup:
            self.soup = soup
        else:
            raise ValueError("Either html_content or soup must be provided")

        self.job_detail = self.soup.find("div", class_="noo-main")
        self.job_company = self.soup.find("div", class_="noo-sidebar-wrap")

    def parse(self):
        """Main method to parse job details"""
        if not self.job_detail or not self.job_company:
            return None

        title = self._get_title()
        if not title:
            return None

        company_name = self._get_company_name()
        if not company_name:
            return None

        description = self._get_description()
        if not description:
            return None

        location_info = self._get_location_info()
        job_type = self._get_job_type()
        categories = self._get_categories()
        date_info = self._get_date_info("job-date__posted")
        application_deadline = self._get_date_info("job-date__closing")

        third_party_metadata = {
            "categories": categories,
            "company_name": company_name,
        }

        return GamJob(
            title=title,
            job_type=job_type,
            created_at=date_info,
            description=description,
            country=location_info["country"],
            address=location_info["address"],
            application_deadline=application_deadline,
            third_party_metadata=third_party_metadata,
            required_skills=categories,
            benefits=[],
            pricing={},
        )

    def _get_title(self):
        """Extract job title"""
        title_elm = self.job_detail.find("h1", class_="page-title")
        if title_elm:
            return list(title_elm.children)[0].text.strip()
        return None

    def _get_company_name(self):
        """Extract company name"""
        company_name_elm = self.job_company.find("h3", class_="company-title")
        if company_name_elm:
            return company_name_elm.text.strip()
        return None

    def _get_description(self):
        """Extract job description"""
        description = self.job_detail.find("div", attrs={"itemprop": "description"})
        if not description:
            return None

        description = description.prettify()
        if isinstance(description, bytes):
            description = description.decode(self.soup.original_encoding)
        return description

    def _get_job_type(self):
        """Extract job type"""
        job_type_elem = self.job_detail.find("span", class_="job-type")
        return job_type_elem.text.strip() if job_type_elem else "N/A"

    def _get_location_info(self):
        """Extract location information"""
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

    def _get_date_info(self, class_name):
        """Extract date information"""
        date_elem = self.job_detail.find("span", class_=class_name)
        return date_elem.text.strip() if date_elem else "N/A"

    def _get_categories(self):
        """Extract job categories"""
        categories = []
        categories_elm = self.job_detail.select("span.job-category a")
        if categories_elm:
            for anchor in categories_elm:
                _v = anchor.text.strip()
                if _v:
                    categories.append(_v)
        return categories


class GamJobScraper:

    _base_url = "https://gamjobs.com"
    _headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    }

    def _clean_system_threads(self):
        """
        Clean up any zombie threads that may be left over from ThreadPoolExecutor
        """
        current = threading.current_thread()
        for thread in threading.enumerate():
            if thread != current and not thread.daemon:
                try:
                    thread.join(timeout=1.0)
                except Exception:
                    pass

    def _get_job_links(self):
        response = requests.get(f"{self._base_url}/jobs", headers=self._headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        _a = soup.find_all("a", class_="job-details-link")
        job_links = [link["href"] for link in _a]

        print(job_links)
        return job_links

    def _get_job_link_page(self, links: List[str]):

        def _thread(_link: str):
            response = requests.get(_link, headers=self._headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            return soup

        soups: List[BeautifulSoup] = []

        # Using ThreadPoolExecutor for concurrent execution
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tasks and get futures
            soups_fixtures = [executor.submit(_thread, link) for link in links]

            # Collect results as they complete
            for _soup in soups_fixtures:
                result = _soup.result()
                if result:
                    soups.append(result)

        self._clean_system_threads()
        print(soups)
        return soups

    def scrape(self):

        def process_link(soup: BeautifulSoup) -> GamJob:
            parser = GamJobParser(soup=soup)
            job = parser.parse()
            return job

        jobs: List[GamJob] = []

        links = self._get_job_links()
        soups = self._get_job_link_page(links)

        # Clear any zombie threads

        with ThreadPoolExecutor(max_workers=3) as executor:
            jobs_fixtures = [executor.submit(process_link, soup) for soup in soups]

            # Collect results as they complete
            for _job in jobs_fixtures:
                result = _job.result()
                if result:
                    jobs.append(result)

        self._clean_system_threads()
        return jobs


if __name__ == "__main__":

    pass

    # scrapper = GamJobScraper()
    # print(scrapper.scrape())
    

    # files = ["jobs", "jobs2", "jobs3", "jobs4"]

    # for file in files:
    #     with open(f"{file}.html", "r", encoding="utf-8") as file:
    #         content = file.read()
    #         parser = GamJobParser(content)
    #         data = parser.parse()
    #         print(data, end="\n\n")
