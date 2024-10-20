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
            user = User.objects.get(email=email)
            return
        except User.DoesNotExist:
            user = User()
            user.is_staff = True
            user.is_active = True
            user.is_superuser = True
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.gender = gender

            try:
                User.objects.get(username="super-admin")
                user.username = "super-admin" + str(random.randint(10000, 99999))
            except User.DoesNotExist:
                user.username = "super-admin"

            if avatar:
                user.avatar = avatar

            user.set_password(password)
            user.save()

        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            raise e
