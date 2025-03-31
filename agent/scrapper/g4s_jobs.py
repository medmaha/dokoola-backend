import re
from datetime import datetime
from typing import Callable, Dict, List, Optional, Tuple

from agent.scrapper.base import JobParser, JobScraper, ScrapedJob


class G4SJobParser(JobParser):
    """
    A parser for G4S job listings.
    """

    def __init__(
        self,
        job_url: Optional[str] = "",
        page_source: Optional[str] = None,
        callback: Callable[[ScrapedJob], None] = None,
    ):
        super().__init__(
            job_url=job_url,
            callback=callback,
            page_source=page_source,
            parsers=["bs4", "percel"],
        )
        # Extract the title and metadata container from the HTML
        self.title_tag = self.bs4.find("h1")
        self.metadata_container = (
            self.title_tag.find_next("span") if self.title_tag else None
        )

    def _get_title(self) -> str:
        title_tag = self.title_tag
        if title_tag:
            full_title = title_tag.get_text(strip=True)
            parts = full_title.split("|")
            return parts[0].strip() if parts else full_title.strip()
        return ""

    def _get_company_name(self):
        return "G4S"

    def _get_description(self):
        # Try multiple possible selectors for the job description
        selectors = [
            "#main-content > div.card.cms-content > div > div > div.col-12.col-lg-9.border-right",
            ".card.cms-content .col-12.col-lg-9.border-right",
            ".cms-content .col-lg-9",
            "#main-content .card.cms-content",
        ]

        for selector in selectors:
            desc_elm = self.bs4.select(selector)
            if desc_elm:
                desc_container = desc_elm[0]
                # First try to find the content in a nested div
                content_div = desc_container.find("div")
                if content_div:
                    description = content_div.get_text(separator="\n", strip=True)
                    if description:
                        return description

                # If no nested div or empty content, get text from container itself
                description = desc_container.get_text(separator="\n", strip=True)
                if description:
                    return description

        # Fallback: try to find any div with substantial content
        main_content = self.bs4.find(id="main-content")
        if main_content:
            content_divs = main_content.find_all("div", class_="card")
            for div in content_divs:
                description = div.get_text(separator="\n", strip=True)
                if len(description) > 100:  # Ensure we have substantial content
                    return description

        return "No description found"

    def _extract_field(self, text: str, field_label: str) -> str:
        pattern = rf"{field_label}:\s*(.*?)(?=(?:Location:|Salary:|Posted:|Closes:|Job Type:|Business Unit:|Region / Division:|Reference:)|$)"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _get_job_type(self) -> str:
        if self.metadata_container:
            text = self.metadata_container.get_text(" ", strip=True)
            return self._extract_field(text, "Job Type")
        return "Not specified"

    def _get_location_info(self) -> Dict[str, str]:
        if self.metadata_container:
            text = self.metadata_container.get_text(" ", strip=True)
            location = self._extract_field(text, "Location")
            return {
                "address": location or "Not specified",
                "country": location or "Not specified",
            }
        return {"address": "Not specified", "country": "Not specified"}

    def _get_created_at(self) -> datetime:
        result = None
        try:
            xpath_query = (
                'string(//*[@id="main-content"]/div[2]/div/div/div[1]/span)/text()[3]'
            )
            result = self.get_element_by_xpath(xpath_query)
            if result:
                return datetime.strptime(result, "%d %b %Y")
        except Exception as e:
            print(f"Error parsing posted date: {result} Error: {e}")
        return datetime.now()

    def _get_application_deadline(self) -> datetime:
        try:
            xpath_query = 'normalize-space(//*[@id="main-content"]/div[2]/div/div/div[1]/span/text()[4])'
            result = self.get_element_by_xpath(xpath_query)
            if result:
                return datetime.strptime(result, "%d %b %Y")
        except Exception as e:
            print(f"Error parsing closing date: {e}")
        return datetime.now()

    def _get_categories(self) -> List[str]:
        title_tag = self.bs4.find("h2", class_="text-primary h5 mb-1")
        if title_tag:
            parts = title_tag.get_text(strip=True).split("|")
            if len(parts) >= 2:
                return [parts[1].strip()]
        return []


class G4SJobScraper(JobScraper):
    _BASE_URL = "https://careers.g4s.com/en/"

    def __init__(self, base_url: str = _BASE_URL, to_json=False, max_jobs=None):
        super().__init__(
            max_jobs=max_jobs,
            base_url=base_url,
            to_json=to_json,
            parser=G4SJobParser,
            pathname="/jobs",
            job_link_selectors=".list-group-item-action",
        )
