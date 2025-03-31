import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Callable, List, Optional, final

from selenium.webdriver.common.by import By

from .driver import ScaperWebDriver
from .models import ScrapedJob
from .parser import JobParser
from .utils import get_job_type_or_other, kill_zombie_threads, logger


class JobScraper(ScaperWebDriver):
    def __init__(
        self,
        parser: JobParser,
        pathname: str,
        job_link_selectors: str,
        max_jobs: Optional[int] = 20,
        to_json: Optional[bool] = False,
        base_url: Optional[str] = "https://gamjobs.com",
    ):
        super().__init__()
        # Ensure parser implements a parse method
        if not hasattr(parser, "parse"):
            raise ValueError("Parser must implement a parse method")

        self.__to_json = to_json
        self.__base_url = base_url
        self.__max_length = max_jobs
        self.__max_workers = int(os.getenv("MAX_SCRAPER_WORKERS", 2))

        self.parser: JobParser = parser

        self.links: List[str] = []
        self.jobs: List[ScrapedJob] = []

        self.processed_links = set()

        self.end_time = 0
        self.start_time = 0

        self.pathname = pathname
        self.job_link_selectors = job_link_selectors

        self.__exeption_callback = lambda x: None

        # Set up Selenium WebDriver
        self._start_driver()

    def set_exeption_callback(self, callback: Callable[[List[ScrapedJob]], None]):
        self.__exeption_callback = callable

    def _log_scape_timer(self):

        if not self.start_time:
            self.start_time = time.time()
            return

        self.end_time = time.time()
        elapsed_time = self.end_time - self.start_time
        print("==================================================================")
        logger.info(f"Scraping completed in {elapsed_time:.2f} seconds")
        logger.info(
            "Scraping Info Jobs: {} Links: {}".format(len(self.jobs), len(self.links))
        )
        print("==================================================================")

    def _get_job_links_raw(self) -> None:
        """Get job links from the main page using Selenium"""

        jobs_page_link = f"{self.__base_url}{self.pathname}"
        self.driver.get(jobs_page_link)
        links = self.driver.find_elements(By.CSS_SELECTOR, f"{self.job_link_selectors}")
        logger.info("Links:", len(links))
        self.links = [
            link.get_attribute("href") for link in links if link.get_attribute("href")
        ][: self.__max_length]

    def _get_job_parser(self, url: str, index) -> JobParser | None:
        """Parse individual job parser."""

        if url in self.processed_links:
            return None
        self.processed_links.add(url)

        try:
            self.driver.get(url)
            job_parser = self.parser(
                job_url=url,
                page_source=self.driver.page_source,
                callback=lambda x: self.jobs.append(x),
            )
            return job_parser

        except Exception as e:
            logger.error(f"Error parsing job (JobScraper): {str(e)}")
            return None

    def _exucute_scrapping(self) -> None:
        """Fetch job pages concurrently with Selenium"""
        with ThreadPoolExecutor(max_workers=self.__max_workers) as executor:
            for index, link in enumerate(self.links, start=1):
                job_parser = self._get_job_parser(link, index)
                if job_parser is not None:
                    executor.submit(job_parser.parse)

        kill_zombie_threads()

    def scrape(self) -> List[ScrapedJob]:
        """Scrape all jobs from the website using Selenium"""

        self._log_scape_timer()

        self._get_job_links_raw()
        if not self.links:
            return self.jobs
        self._exucute_scrapping()

        return self.jobs

    def __enter__(self, on_error_callback=None):
        if on_error_callback is not None:
            self.set_exeption_callback(on_error_callback)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                # self.__exeption_callback(self.jobs, exc_type=exc_type, exc_val=exc_type, exc_tb=exc_tb)
                self.__exeption_callback(self.jobs)
                logger.error(
                    f"[Error] while scraping jobs [{self.__class__.__name__}]: {str(exc_val)}"
                )
        except Exception as e:
            logger.error(f"Error in __exit__: {str(e)}")
        finally:
            self._log_scape_timer()
            self._close_driver()
