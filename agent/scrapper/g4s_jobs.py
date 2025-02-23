import re
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from agent.scrapper.base import JobParser, JobScraper

class G4SJobParser(JobParser):
    """
    A parser for G4S job listings.
    """
    def __init__(self, url: Optional[str] = "", html_content: Optional[str] = None, soup: Optional[BeautifulSoup] = None):
        super().__init__(url=url, html_content=html_content, soup=soup)
        title_tag = self.soup.find("h2", class_="text-primary h5 mb-1")
        self.metadata_container = title_tag.find_next("span") if title_tag else None

    def _get_title(self) -> str:
        title_tag = self.soup.find("h2", class_="text-primary h5 mb-1")
        if title_tag:
            full_title = title_tag.get_text(strip=True)
            parts = full_title.split("|")
            return parts[0].strip() if parts else full_title.strip()
        return ""

    def _get_company_name(self) -> str:
        return "G4S"

    def _get_description(self) -> str:
        desc_container = self.soup.find("div", class_="col-12 col-lg-9 border-right")
        if desc_container:
            content_div = desc_container.find("div")
            return content_div.get_text(separator="\n", strip=True) if content_div else desc_container.get_text(separator="\n", strip=True)
        return ""
    
    def _extract_field(self, text: str, field_label: str) -> str:
        pattern = fr"{field_label}:\s*(.*?)(?=(?:Location:|Salary:|Posted:|Closes:|Job Type:|Business Unit:|Region / Division:|Reference:)|$)"
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
            return {"address": location or "Not specified", "country": location or "Not specified"}
        return {"address": "Not specified", "country": "Not specified"}

    def _get_created_at(self) -> datetime:
        if self.metadata_container:
            text = self.metadata_container.get_text(" ", strip=True)
            date_str = self._extract_field(text, "Posted")
            try:
                return datetime.strptime(date_str, "%d %b %Y")
            except Exception as e:
                print(f"Error parsing posted date: {e}")
        return datetime.now()

    def _get_application_deadline(self) -> datetime:
        if self.metadata_container:
            text = self.metadata_container.get_text(" ", strip=True)
            date_str = self._extract_field(text, "Closes")
            try:
                return datetime.strptime(date_str, "%d %b %Y")
            except Exception as e:
                print(f"Error parsing closing date: {e}")
        return datetime.now()

    def _get_categories(self) -> List[str]:
        title_tag = self.soup.find("h2", class_="text-primary h5 mb-1")
        if title_tag:
            parts = title_tag.get_text(strip=True).split("|")
            if len(parts) >= 2:
                return [parts[1].strip()]
        return []


class G4SJobScraper(JobScraper):
    _BASE_URL = "https://careers.g4s.com/en/"

    def __init__(
        self, max_workers: int = 3, base_url: str = _BASE_URL, to_json=False
    ):
        super().__init__(
            max_workers=max_workers,
            base_url=base_url,
            to_json=to_json,
            parser=G4SJobParser,
        )

    def scrape(self):
        return super().scrape(pathname="/jobs", link_class="list-group-item-action")
