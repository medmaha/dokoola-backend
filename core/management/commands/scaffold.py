import sys
from typing import Any

from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> str | None:
        from django.conf import settings
        from django.core.management import execute_from_command_line

        from core.management.seeders import categories_seeding

        sys.stdout.write(
            self.style.SUCCESS(
                "------------------------------- Executing Application Scaffolding -------------------------------\n"
            )
        )

        # Create database migrations
        argv = ["manage.py", "makemigrations"]
        execute_from_command_line(argv)

        # Apply database migrations
        argv = ["manage.py", "migrate"]
        execute_from_command_line(argv)

        # Populate database with initial category data
        categories_seeding()
        sys.stdout.write("✅ Database seeding applied successfully\n")

        # Create superuser
        argv = ["manage.py", "superadmin"]
        execute_from_command_line(argv)
        sys.stdout.write("✅ Superuser account created successfully\n")

        # Collect static files
        argv = ["manage.py", "collectstatic", "--noinput"]
        execute_from_command_line(argv)
        sys.stdout.write("✅ Static files collected and saved successfully\n")
        sys.stdout.write(
            self.style.SUCCESS(
                "------------------------------- Done Scaffolding Application -------------------------------\n"
            )
        )
