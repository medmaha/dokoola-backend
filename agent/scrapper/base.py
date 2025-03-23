import datetime
import logging
import random
import threading
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import ClassVar, Dict, Iterator, List, Optional, Tuple, final

import requests
from bs4 import BeautifulSoup
from ratelimit import limits, sleep_and_retry


class Logging:
    def error(self, *args, **kwargs):
        print(*args, **kwargs)

    def info(self, *args, **kwargs):
        print(*args, **kwargs)


logger = Logging()


@dataclass
class ScrapedJob:
    url: str
    title: str
    description: str
    address: str
    job_type: str
    pricing: dict
    country: dict
    benefits: dict
    created_at: datetime
    job_type_other: Optional[str]
    required_skills: List[str]
    third_party_metadata: dict
    application_deadline: datetime

    class ScrappedJobDict(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __getattr__(self, name):
            return self.get(name, None)

        def __setattr__(self, name, value):
            self[name] = value

    def __iter__(self) -> Iterator[Tuple[str, object]]:
        for field in self.__dataclass_fields__:
            yield field, getattr(self, field)

    def to_json(self):
        return self.ScrappedJobDict(self)


def request_headers():
    # Rotate IPs/user-agents to bypass blocks
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    }


# Rate limit: 1 request per second
@sleep_and_retry
@limits(calls=1, period=1)
def rate_limited_request(
    url: str, __headers: Optional[Dict[str, str]] | None = None
) -> requests.Response:
    """Make a rate-limited HTTP request"""

    headers = request_headers()
    if __headers:
        headers.update(__headers)

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return response


class JobParser:
    def __init__(
        self,
        url: Optional[str] = "",
        html_content: Optional[str] = None,
        soup: Optional[BeautifulSoup] = None,
    ):
        self.url = url
        if html_content:
            self.soup = BeautifulSoup(html_content, "html.parser")
        elif soup:
            self.soup = soup
        else:
            raise ValueError("Either html_content or soup must be provided")

        self.job_detail = self.soup.find("div", class_="noo-main")
        self.job_company = self.soup.find("div", class_="noo-sidebar-wrap")

    @abstractmethod
    def _get_title(self):
        """Extract job title"""
        pass

    @abstractmethod
    def _get_company_name(self):
        """Extract company name"""
        pass

    @abstractmethod
    def _get_description(self):
        """Extract job description"""
        pass

    @abstractmethod
    def _get_job_type(self):
        """Extract job type"""
        pass

    @abstractmethod
    def _get_job_type_other(self, job_type: str):
        """Extract job type other"""
        pass

    @abstractmethod
    def _get_location_info(self):
        """Extract location information"""
        pass

    @abstractmethod
    def _get_created_at(self):
        """Extract created at"""
        pass

    @abstractmethod
    def _get_application_deadline(self):
        """Extract application deadline"""
        pass

    @abstractmethod
    def _get_categories(self):
        """Extract job categories"""
        pass

    @abstractmethod
    def _required_skills(self):
        """Extract job categories"""
        pass

    def _get_job_pricing(
        self, job_description: Optional[str] = None
    ) -> dict[str, str | int]:
        return {}

    def _get_job_benefits(self, job_description: Optional[str] = None) -> list:
        return []

    def _get_site_name(self) -> str:
        return ""

    @final
    def parse(self) -> Optional[ScrapedJob]:
        """
        Parse job details from HTML content
        Returns:
            Optional[GamJob]: Parsed job object or None if parsing fails
        """
        try:
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
            required_skills = self._required_skills()
            created_at = self._get_created_at()
            application_deadline = self._get_application_deadline()

            third_party_metadata = {
                "site_url": self.url,
                "site_name": self._get_site_name(),
                "categories": categories,
                "company_name": company_name,
            }

            job_type, job_type_other = self._get_job_type_other(job_type)

            return ScrapedJob(
                url=self.url,
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
        except Exception as e:
            logger.error(f"Error parsing job (JobParser): {str(e)}")
            return None


class JobScraper:
    def __init__(
        self,
        parser: JobParser,
        max_workers: int = 3,
        to_json=False,
        base_url: str = "https://gamjobs.com",
        headers: Optional[Dict[str, str]] = None,
    ):

        # make the sure parser is includes a parse method
        if not hasattr(parser, "parse"):
            raise ValueError("Parser must implement a parse method")

        self._to_json = to_json
        self._base_url = base_url
        self._max_workers = max_workers
        self._session = requests.Session()
        self.parser: JobParser = parser
        self._headers = headers
        self.soups: List[Tuple[str, BeautifulSoup]] = []

    @final
    def __kill_zombie_threads(self):
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

    @final
    def __get_job_links_raw(self, soup: BeautifulSoup, pathname: str) -> List[str]:
        """
        Get job links from the main page hard core
        Retrieve any link that has a href attribute of {base_url}/{pathname}/{*}
        The as any other path/subpath
        """
        import re

        return [
            link["href"]
            for link in soup.find_all(
                "a", href=re.compile(f"{self._base_url}/{pathname}/.*")
            )
        ]

    @final
    def __links(self, pathname: str, link_class: str) -> List[str]:
        """Fetch and extract job links from the main page"""

        try:
            response = rate_limited_request(f"{self._base_url}{pathname}")
            soup = BeautifulSoup(response.text, "html.parser")
            job_links = [link["href"] for link in soup.find_all("a", class_=link_class)]

            if len(job_links) < 1:
                job_links = self.__get_job_links_raw(soup, pathname)

            logger.info(f"Found {len(job_links)} job links")
            return job_links

        except Exception as e:
            logger.error(f"Error fetching job links: {str(e)}")
            return []

    @final
    def __soups(self, links: List[str]) -> List[Tuple[str, BeautifulSoup]]:
        """Fetch job pages concurrently with rate limiting"""

        soups: List[BeautifulSoup] = []

        def _fetch_page(url: str) -> Optional[BeautifulSoup]:
            try:
                response = rate_limited_request(url, self._headers)
                return (url, BeautifulSoup(response.text, "html.parser"))
            except Exception as e:
                logger.error(f"Error fetching {url}: {str(e)}")
                return None

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_to_url = {executor.submit(_fetch_page, link): link for link in links}

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    soup = future.result()
                    if soup:
                        soups.append(soup)
                except Exception as e:
                    logger.error(f"Error processing {url}: {str(e)}")

        self.__kill_zombie_threads()

        # self.soups = soups

        return soups

    @final
    def __soup(self, url: str) -> BeautifulSoup:
        """Get the soup of a given url"""

        for url_and_soup in self.soups:
            url, soup = url_and_soup
            if url == url:
                return soup

    def scrape(self, pathname: str, link_class: str) -> List[ScrapedJob]:
        """
        Scrape all jobs from the website
        Returns:
            List[ScrapedJob]: List of parsed job objects
        """

        jobs: List[ScrapedJob] = []

        try:
            links = self.__links(pathname, link_class)
            if not links:
                return jobs

            soups = self.__soups(links)

            logger.info(f"Soups: {soups}")

            self._session.close()

            with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                future_to_soup = {
                    executor.submit(self.parser(url=soup[0], soup=soup[1]).parse): soup
                    for soup in soups
                }

                for future in as_completed(future_to_soup):
                    try:
                        job = future.result()
                        logger.info(f"Job: {job}")
                        if job:
                            if self._to_json:
                                jobs.append(job.to_json())
                            else:
                                jobs.append(job)
                    except Exception as e:
                        logger.error(f"Error parsing job (JobScraper): {str(e)}")

            logger.info(f"Successfully scraped {len(jobs)} jobs")

            self.__kill_zombie_threads()

            return jobs

        except Exception as e:
            logger.error(f"Error in scrape process: {str(e)}")
            return jobs
