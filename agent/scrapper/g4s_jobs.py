import re
from typing import Callable, Optional

from bs4 import BeautifulSoup
from django.utils import timezone

from agent.scrapper.base import JobParser, JobScraper, ScrapedJob


class G4SJobParser(JobParser):

    def __init__(
        self,
        job_url: Optional[str] = "",
        page_source: Optional[str] = "",
        callback: Callable[[ScrapedJob], None] = None,
    ):

        super().__init__(
            parsers=["bs4"],
            job_url=job_url,
            callback=callback,
            page_source=page_source,
        )

        self.metadata_container = self.bs4.select_one("h2~span")

        if not self.metadata_container:
            self.metadata_container = self.bs4.select_one(
                ".d-flex.flex-column.flex-lg-row.mb-2"
            )

    def _get_title(self):
        title_tag = self.bs4.select_one("h1").text
        if not title_tag:
            return None
        return title_tag.strip()

    def _get_company_name(self):
        return "G4S"

    def _get_description(self):
        desc_container = self.bs4.select_one("div.col-12.border-right")
        # desc_container = self.bs4.find("div", class_="col-12 col-lg-9 border-right")
        if desc_container:
            soup = self.sanitize_text(str(desc_container), elements=["img"])
            content_div = soup.find("div")
            return (
                content_div.get_text(separator="\n", strip=True)
                if content_div
                else desc_container.get_text(separator="\n", strip=True)
            )
        return ""

    def _get_job_type(self):
        if self.metadata_container:
            text = self.metadata_container.get_text(" ", strip=True)
            return self.__extract_field(text, "Job Type")
        return "Not specified"

    def _get_location_info(self):
        if self.metadata_container:
            text = self.metadata_container.get_text(" ", strip=True)
            location = self.__extract_field(text, "Location")
            return {
                "address": location or "Not specified",
                "country": location or "Not specified",
            }
        return {"address": "Not specified", "country": "Not specified"}

    def _get_created_at(self):
        if self.metadata_container:
            text = self.metadata_container.get_text(" ", strip=True)
            date_str = self.__extract_field(text, "Posted")
            try:
                date_str = timezone.datetime.strptime(date_str, "%d %b %Y")
                return date_str
            except Exception as e:
                print(f"Error parsing posted date: {e}")
        return timezone.datetime.now()

    def _get_application_deadline(self):
        if self.metadata_container:
            text = self.metadata_container.get_text(" ", strip=True)
            date_str = self.__extract_field(text, "Closing")
            try:
                return timezone.datetime.strptime(date_str, "%d %b %Y")
            except Exception as e:
                print(f"Error parsing closing date: {e}")
        return timezone.datetime.now()

    def _get_categories(self):
        title_tag = self.bs4.find("h2", class_="text-primary h5 mb-1")
        if title_tag:
            parts = title_tag.get_text(strip=True).split("|")
            if len(parts) >= 2:
                return [parts[1].strip()]
        return []

    def _get_required_skills(self):
        return []

    def __extract_field(self, text: str, field_label: str) -> str:
        pattern = rf"{field_label}:\s*(.*?)(?=(?:Location:|Salary:|Posted:|Closes:|Job Type:|Business Unit:|Region / Division:|Reference:)|$)"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).replace("|", "").strip() if match else ""


class G4SJobScraper(JobScraper):

    _BASE_URL = "https://careers.g4s.com/en/"

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
            parser=G4SJobParser,
            job_link_selectors=".list-group-item-action",
        )

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
