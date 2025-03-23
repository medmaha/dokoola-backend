import os
import random
from typing import Any

from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> str | None:
        from users.models import User

        email = os.getenv("SUPER_ADMIN_EMAIL")
        if not email:
            raise Exception("SUPER_ADMIN_EMAIL env var not set")
        password = os.getenv("SUPER_ADMIN_PASSWORD")
        if not password:
            raise Exception("SUPER_ADMIN_PASSWORD env var not set")

        first_name = os.getenv("SUPER_ADMIN_FIRST_NAME", "Super")
        last_name = os.getenv("SUPER_ADMIN_LAST_NAME", "Admin")
        gender = os.getenv("SUPER_ADMIN_GENDER", "MALE")
        avatar = os.getenv("SUPER_ADMIN_AVATAR")

        try:
            user = User.objects.filter(email=email).first()
            if user:
                user.first_name = first_name
                user.last_name = last_name
                user.avatar = avatar
                user.is_staff = True
                user.is_active = True
                user.is_superuser = True
                user.password = password
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        self.style.SUCCESS("Superadmin updated successfully")
                    )
                )

                return

            user = User()
            user.is_staff = True
            user.is_active = True
            user.is_superuser = True
            user.email = email
            user.avatar = avatar
            user.first_name = first_name
            user.last_name = last_name
            user.gender = gender
            user.username = "super-admin" + str(random.randint(10000, 99999))
            user.password = password
            user.save()

        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            raise e
