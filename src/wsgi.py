
# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")

# application = get_wsgi_application()


import os
from django.core.wsgi import get_wsgi_application

from whitenoise import WhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")

from django.conf import settings

application = get_wsgi_application()
application = WhiteNoise(application, root=settings.STATIC_ROOT, )
application.add_files(settings.BASE_DIR / "public", prefix="more-files/")