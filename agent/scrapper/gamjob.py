from datetime import datetime
from typing import Callable, List, Optional

from bs4 import BeautifulSoup
from django.utils import timezone

from agent.scrapper.base import JobParser, JobScraper, ScrapedJob


class GamJobParser(JobParser):
    def __init__(
        self,
        job_url: Optional[str] = "",
        page_source: Optional[str] = None,
        callback: Callable[[ScrapedJob], None] = None,
    ):
        super().__init__(job_url=job_url, callback=callback)

    def _get_title(self):
        title_elm = self.bs4.find("h1", class_="page-title")
        if title_elm:
            return (
                list(title_elm.children)[0].text.strip().replace("(Re-Advertised)", "")
            )
        return None

    def _get_company_name(self):
        company_name_elm = self.bs4.find("h3", class_="company-title")
        if company_name_elm:
            return company_name_elm.text.strip()
        return None

    def _get_description(self):
        description = self.bs4.find("div", attrs={"itemprop": "description"})
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
        return timezone.datetime.strptime(_date, "%B %d, %Y")

    def _get_application_deadline(self):
        date_elem = self.bs4.find("span", class_="job-date__closing")

        if not date_elem:
            return None

        # Sample "- March 14, 2025"
        _date = str(date_elem.text.strip()).replace("- ", "")
        return datetime.strptime(_date, "%B %d, %Y")

    def _required_skills(self):
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

    def __init__(
        self,
        max_jobs: Optional[int] = None,
        base_url: str = _BASE_URL,
        to_json=False,
        writefile: Optional[bool] = False,
    ):
        super().__init__(
            base_url=base_url,
            to_json=to_json,
            max_jobs=max_jobs,
            parser=GamJobParser,
            pathname="/jobs",
            job_link_selectors=".job-details-link",
        )

        self.__writefile = writefile

    def scrape(self):
        """
        Scrape all jobs from the website
        Returns:
            List[GamJob]: List of parsed job objects
        """

        jobs = super().scrape()
        self._update_metadata()

        if self.__writefile:
            self._write_jobs_in_file()

        return self.jobs

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
                    "description": " ".join(description)[:max_length],
                }
            )

    def _write_jobs_in_file(self) -> None:
        """Inject job results into a file."""

        # Create a basic HTML structure for displaying the job results
        html_content = f"""
            <html><body><h1>Job Results</h1>
            <br/>
            <p>Total Links: {len(self.links)}</p>
            <p>Processed Links: {len(self.process_links)}</p>
            <br/>
            <br/>
            <ol>
        """

        for job in self.jobs:
            html_content += f"""
            <li>
                <strong>{job.title}</strong><br>
                <b>Company:</b> {job.third_party_metadata.get('company_name', 'N/A')}<br>
                # <b>Description:</b> {job.third_party_metadata.get('description', 'No description available')}<br>
                <b>Location:</b> {job.address}<br>
                <b>Job Type:</b> {job.job_type}<br>
                <b>Job Type Other:</b> {job.job_type_other}<br>
                <b>Application Deadline:</b> {job.application_deadline}<br>
                <b>Application CreatedAt:</b> {job.created_at}<br>
                <b>Source:</b> <a href="{job.url}" target="_blank">View Job</a>
            </li>
            <br>
            <hr>
            <br>
            """

        html_content += "</ol>"

        js_script = f"""
            <pre>
                <code id='code'></code>
            </pre>
            <script>
                const jobs = {[job.to_json() for jobs in self.jobs]}
                document.getElementById('code').innerHTML = JSON.stringify(jobs, null, 4)
            </script>
        """

        html_content += f"{js_script}</body></html>"
        # Inject the HTML into the browser window
        # self.driver.execute_script(f"document.body.innerHTML = `{html_content}`;")
        # self.driver.set_script_timeout()

        with open("scraper.html", "w", encoding="utf-16") as file:
            file.write(html_content)
