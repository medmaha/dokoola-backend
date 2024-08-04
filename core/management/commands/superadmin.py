import os
from typing import Any
from django.core.management import BaseCommand

class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> str | None:
        from users.models import User

        email = os.getenv('SUPER_ADMIN_EMAIL')
        if not email:
            raise Exception('SUPER_ADMIN_EMAIL env var not set')
        password = os.getenv('SUPER_ADMIN_PASSWORD')
        if not password:
            raise Exception('SUPER_ADMIN_PASSWORD env var not set')
    
        first_name = os.getenv('SUPER_ADMIN_FIRST_NAME', 'Super')
        last_name = os.getenv('SUPER_ADMIN_LAST_NAME', 'Admin')
        gender = os.getenv('SUPER_ADMIN_GENDER', 'MALE')
        avatar = os.getenv('SUPER_ADMIN_AVATAR')

        print("Creating Super user account...")

        try:
            user = User.objects.get(email=email)
            if not user.is_superuser:
                raise Exception('User with email "%s" already exists' % email)        
            self.stdout.write(self.style.SUCCESS('Superadmin already exists'))
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
            
            if avatar:
                user.avatar = avatar

            user.set_password(password)
            user.save()

            self.stdout.write(self.style.SUCCESS('Superadmin status updated'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            raise e