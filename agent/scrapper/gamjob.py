from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import threading
import logging
from typing import List, Optional, Dict
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from ratelimit import limits, sleep_and_retry

# logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Rate limit: 1 request per second
@sleep_and_retry
@limits(calls=1, period=1)
def rate_limited_request(url: str, headers: Dict[str, str]) -> requests.Response:
    """Make a rate-limited HTTP request"""
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response

class GamJobParser:
    def __init__(self, html_content: Optional[str] = None, soup: Optional[BeautifulSoup] = None):
        if html_content:
            self.soup = BeautifulSoup(html_content, "html.parser")
        elif soup:
            self.soup = soup
        else:
            raise ValueError("Either html_content or soup must be provided")

        self.job_detail = self.soup.find("div", class_="noo-main")
        self.job_company = self.soup.find("div", class_="noo-sidebar-wrap")

    def parse(self) -> Optional[GamJob]:
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
        except Exception as e:
            logger.error(f"Error parsing job: {str(e)}")
            return None

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
    def __init__(self, max_workers: int = 3, base_url: str = "https://gamjobs.com"):
        self._base_url = base_url
        self._max_workers = max_workers
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        }
        self._session = requests.Session()

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

    def _get_job_links(self) -> List[str]:
        """Fetch and extract job links from the main page"""
        try:
            response = rate_limited_request(f"{self._base_url}/jobs", self._headers)
            soup = BeautifulSoup(response.text, "html.parser")
            job_links = [link["href"] for link in soup.find_all("a", class_="job-details-link")]
            logger.info(f"Found {len(job_links)} job links")
            return job_links
        except Exception as e:
            logger.error(f"Error fetching job links: {str(e)}")
            return []

    def _get_job_link_page(self, links: List[str]) -> List[BeautifulSoup]:
        """Fetch job pages concurrently with rate limiting"""
        soups: List[BeautifulSoup] = []
        
        def _fetch_page(url: str) -> Optional[BeautifulSoup]:
            try:
                response = rate_limited_request(url, self._headers)
                return BeautifulSoup(response.text, "html.parser")
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
        self._clean_system_threads()
        return soups

    def scrape(self) -> List[GamJob]:
        """
        Scrape all jobs from the website
        Returns:
            List[GamJob]: List of parsed job objects
        """
        jobs: List[GamJob] = []
        
        try:
            links = self._get_job_links()
            if not links:
                return jobs

            soups = self._get_job_link_page(links)
            
            with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                future_to_soup = {executor.submit(GamJobParser(soup=soup).parse): soup 
                                for soup in soups}
                
                for future in as_completed(future_to_soup):
                    try:
                        job = future.result()
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.error(f"Error parsing job: {str(e)}")

            logger.info(f"Successfully scraped {len(jobs)} jobs")
            self._clean_system_threads()
            return jobs
            
        except Exception as e:
            logger.error(f"Error in scrape process: {str(e)}")
            return jobs
