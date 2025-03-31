from datetime import datetime
from typing import List, Optional

from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from agent.scrapper.base import JobParser, JobScraper, ScrapedJob


class GamJobParser(JobParser):
    def __init__(
        self,
        job_url: str,
        driver: webdriver.Chrome,
    ):
        super().__init__(url=job_url, driver=driver)
        self.driver = driver

    def _get_title(self):
        def clean_title(title: str):
            return title.replace("(Re-Advertised)", "")

        title_elm = self.driver.find_element(By.CSS_SELECTOR, "h1.page-title")
        if title_elm:
            span_elem = title_elm.find_element(By.CSS_SELECTOR, "span.count")
            if span_elem:
                return clean_title(
                    title_elm.text.strip().replace(span_elem.text.strip(), "")
                )
            return clean_title(title_elm.text.strip())
        return None

    def _get_company_name(self):
        company_name_elm = self.driver.find_element(By.CSS_SELECTOR, "h3.company-title")
        if company_name_elm:
            return company_name_elm.text.strip()
        return None

    def _get_description(self):
        description_elm = self.driver.find_element(
            By.CSS_SELECTOR, "div[itemprop='description']"
        )
        if not description_elm:
            return None
        return description_elm.get_attribute("innerHTML")

    def _get_job_type(self):
        job_type_elem = self.driver.find_element(By.CSS_SELECTOR, "span.job-type")
        return job_type_elem.text.strip() if job_type_elem else "N/A"

    def _get_job_type_other(self, job_type: str):
        job_type = (job_type or "").lower()
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

        locations_elm = self.driver.find_elements(
            By.CSS_SELECTOR, "span.job-location a"
        )
        for anchor in locations_elm:
            _v = anchor.text.strip()
            if _v:
                locations.append(_v)

        if locations:
            address = " - ".join(locations[:-1])
            country = {"name": locations[-1]}

        return {"country": country, "address": address}

    def _get_created_at(self):
        date_elem = self.driver.find_element(By.CSS_SELECTOR, "span.job-date__posted")
        if not date_elem:
            return None

        _date = str(date_elem.text.strip()).replace("- ", "")
        return timezone.datetime.strptime(_date, "%B %d, %Y")

    def _get_application_deadline(self):
        date_elem = self.driver.find_element(By.CSS_SELECTOR, "span.job-date__closing")
        if not date_elem:
            return None

        _date = str(date_elem.text.strip()).replace("- ", "")
        return datetime.strptime(_date, "%B %d, %Y")

    def _required_skills(self):
        categories = []
        categories_elm = self.driver.find_elements(
            By.CSS_SELECTOR, "span.job-category a"
        )
        for anchor in categories_elm:
            _v = anchor.text.strip()
            if _v:
                categories.append(_v)
        return categories

    def _get_categories(self):
        categories = []
        # You can use _required_skills here or adapt this to scrape other category-related elements
        return categories


class GamJobScraper(JobScraper):
    __SOURCE = "Gamjobs"
    __BASE_URL = "https://gamjobs.com"
    __job_link_selectors = ".job-details-link"

    def __init__(self, max_workers: int = 3, base_url: str = __BASE_URL, to_json=False):
        super().__init__(
            max_workers=max_workers,
            base_url=base_url,
            to_json=to_json,
            parser=GamJobParser,
        )

    def scrape(self) -> List[ScrapedJob]:
        """
        Scrape all jobs from the website
        Returns:
            List[GamJob]: List of parsed job objects
        """
        scrapper = super()
        scrapper.scrape(pathname="/jobs", job_link_selectors=self.__job_link_selectors)

        self.update_metadata()
        self.render_jobs_in_browser()
        self.__close_driver()

        return self.jobs

    def update_metadata(self) -> None:
        for job in self.jobs:
            # Update third party metadata
            job.third_party_metadata.update(
                {
                    "source": "gamjobs.com",
                    "source_url": job.url,
                }
            )

            # Find the elements in the job description area
            relevant_tags = ["p", "li", "div", "span"]
            description = ""
            seen_content = set()

            max_desc = 300

            for tag_name in relevant_tags:
                elements = self.driver.find_elements(By.TAG_NAME, tag_name)
                for container in elements:
                    text = container.text.strip()

                    if len(text) > 30 and text not in seen_content:
                        seen_content.add(text)
                        description += text + "\n"

                    if (
                        len(description) > max_desc
                    ):  # Stop after accumulating enough description content
                        break
                if len(description) > max_desc:  # Exit outer loop if we're done
                    break

            job.third_party_metadata["description"] = description.strip()

    def render_jobs_in_browser(self) -> None:
        """Inject job results into the browser page."""

        # Create a basic HTML structure for displaying the job results
        html_content = f"""
            <html><body><h1>Job Results</h1>
            <br/>
            <p>Total Links: {len(self.links)}</p>
            <p>Processed Links: {len(self.process_links)}</p>
            <br/>
            <br/>
            <ul>
        """

        for job in self.jobs:
            html_content += f"""
            <ol>
                <strong>{job.title}</strong><br>
                <b>Company:</b> {job.third_party_metadata.get('company_name', 'N/A')}<br>
                # <b>Description:</b> {job.third_party_metadata.get('description', 'No description available')}<br>
                <b>Location:</b> {job.address}<br>
                <b>Job Type:</b> {job.job_type}<br>
                <b>Job Type Other:</b> {job.job_type_other}<br>
                <b>Application Deadline:</b> {job.application_deadline}<br>
                <b>Application CreatedAt:</b> {job.created_at}<br>
                <b>Source:</b> <a href="{job.url}" target="_blank">View Job</a>
            </ol>
            <br>
            <hr>
            <br>
            """

        html_content += "</ul>"

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

        with open("scraper.html", "w") as file:
            file.write(html_content)

    def __close_driver(self) -> None:
        self.driver.quit()
