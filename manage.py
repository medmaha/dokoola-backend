#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    argv = sys.argv.copy()

    # Implement this so i can run my management commands with custom arguments
    # -------------------------------------------------------------------------
    if "-l" in argv:
        argv.remove("-l")
    if "--loaddata" in argv:
        argv.remove("--loaddata")

    if "-d" in argv:
        argv.remove("-d")
    if "--dumpdata" in argv:
        argv.remove("--dumpdata")
    # -------------------------------------------------------------------------

    execute_from_command_line(argv)


if __name__ == "__main__":
    main()
