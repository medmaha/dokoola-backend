import os
from django.conf import settings

if settings.DEBUG:
    ESCROW_API_URL = os.environ.get("ESCROW_SANDBOX_URL")
else:
    ESCROW_API_URL = os.environ.get("ESCROW_API_KEY")

ESCROW_EMAIL = os.environ.get("ESCROW_EMAIL", "")
ESCROW_API_KEY = os.environ.get("ESCROW_API_KEY", "")


def main():
    pass
