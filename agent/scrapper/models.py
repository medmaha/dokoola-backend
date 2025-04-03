import datetime
from dataclasses import dataclass
from typing import Iterator, List, Optional, Tuple

# Logging setup


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

    def __repr__(self):
        return f"<[ScrapedJob]  Title: {self.title} Type: {self.job_type}>"

    def __str__(self):
        return f"Job: {self.title}"
