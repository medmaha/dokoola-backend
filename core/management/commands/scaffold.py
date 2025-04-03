import sys
from typing import Any

from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> str | None:
        from django.core.management import execute_from_command_line

        from core.management.seeders import categories_seeding
        from src.settings.shared import RUNTIME_ENVIRONMENT

        sys.stdout.write(
            self.style.SUCCESS(
                "\n------------------------------- Executing Application Scaffolding -------------------------------\n\n"
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

        # Create Dokoola Agent
        argv = ["manage.py", "create_agent"]
        execute_from_command_line(argv)
        sys.stdout.write("✅ The Dokoola Agent created successfully\n")

        if RUNTIME_ENVIRONMENT == "production":
            # Collect static files
            argv = ["manage.py", "collectstatic", "--noinput"]
            execute_from_command_line(argv)
            sys.stdout.write("✅ Static files collected and saved successfully\n")

        sys.stdout.write(
            self.style.SUCCESS(
                "\n------------------------------- Done Scaffolding Application -------------------------------\n\n"
            )
        )
