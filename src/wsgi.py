import os

from django.core.wsgi import get_wsgi_application

from src.settings.shared import DEBUG, ENVIRONMENT

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")

from django.conf import settings

application = get_wsgi_application()

if not DEBUG and ENVIRONMENT == "production":
    # Only serve static files in production
    from whitenoise import WhiteNoise

    application = WhiteNoise(
        application,
        root=settings.STATIC_ROOT,
    )
    application.add_files(settings.BASE_DIR / "static", prefix="public/")
