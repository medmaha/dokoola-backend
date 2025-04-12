import sys
from typing import Any

from django.core.management import BaseCommand
from django.core.management.base import CommandParser


class Command(BaseCommand):

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--testusers",
            default=0,
            type=int,
            help="A flag, authorizing test-user creation",
        )

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

        with_test_users = options["testusers"]

        if with_test_users:
            error = create_test_users()

            if error:
                sys.stdout.write(self.style.WARNING(error))
            else:
                sys.stdout.write("✅ Created test-users account \n")

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


def create_test_users():
    from talents.models import Talent
    from users.models import User

    try:
        user_123 = User.objects.create_user(
            email="test123@dokoola.com",
            password="testpassword123",
            username="testuser123",
            first_name="Test123",
            last_name="TestUser",
            is_active=True,
        )
        Talent.objects.create(user=user_123)
        user_abc = User.objects.create_user(
            email="testabc@dokoola.com",
            password="testpasswordabc",
            username="testuserabc",
            first_name="TestABC",
            last_name="TestUser",
            is_active=True,
        )
        Talent.objects.create(user=user_abc)
    except Exception as e:
        return str(e)
