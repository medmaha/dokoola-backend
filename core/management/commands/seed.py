from typing import Any
from django.core.management import BaseCommand

class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> str | None:
        from  ..seeders import seeders
        print("Seeding Database initial data...")
        seeders()
