import sys
from typing import Any
from django.core.management import BaseCommand

class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> str | None:
        from django.conf import settings
        from django.core.management import execute_from_command_line

        # Create database migrations
        argv = ["manage.py", "makemigrations"]
        execute_from_command_line(argv)

        # Apply database migrations
        argv = ["manage.py", "migrate"]
        execute_from_command_line(argv)

        # Populate database with initial data
        argv = ["manage.py", "seed"]
        execute_from_command_line(argv)
        sys.stdout.write(self.style.SUCCESS("Seed data created successfully"))

        # Create superuser
        argv = ["manage.py", "superadmin"]
        execute_from_command_line(argv)
        sys.stdout.write(self.style.SUCCESS("Superuser created successfully"))

        # Collect static files
        argv = ["manage.py", "collectstatic", "--noinput"]
        execute_from_command_line(argv)
        sys.stdout.write(self.style.SUCCESS("Static files collected successfully"))
