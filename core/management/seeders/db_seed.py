import os, sys, subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SEEDERS_PATH = os.path.join(BASE_DIR, ".seeds")


execution_order = [
    ("0_users", "users"),
    ("1_reviews", "reviews"),
    ("2_clients", "clients"),
    ("3_freelancers", "freelancers"),
    ("4_core", "core"),
    ("5_jobs", "jobs"),
    ("6_proposals", "proposals"),
    ("7_contracts", "contracts"),
    ("8_projects", "projects"),
    ("9_notifications", "notifications"),
]

execution_order = sorted(execution_order)


def dump_data_from_db():
    """
    Dump data from DATABASE to ./.seeds/{file}.seed.json
    """

    answer = input(
        "Are you sure you want to dump data from DATABASE to ./.seeds/{file}.seed.json? (y/n): "
    )

    if answer.lower() != "y":
        sys.exit()

    for obj in execution_order:
        file, app = obj
        argv = ["python", "manage.py", "dumpdata", app]

        command_output = subprocess.run(
            argv,
            shell=True,
            capture_output=True,
        )

        dump_path = f"{os.path.join(SEEDERS_PATH, file)}.seed.json"

        with open(dump_path, "wb") as f:
            f.write(command_output.stdout)
            print(
                f"✅ Dumped {app.capitalize()} data to ./.seeds/{file}.seed.json from DATABASE"
            )


def load_data_from_db():
    """
    Load data from ./.seeds/{file}.seed.json to DATABASE
    """

    answer = input(
        "Are you sure you want to load data from ./.seeds/{file}.seed.json to DATABASE? (y/n): "
    )

    if answer.lower() != "y":
        sys.exit()

    for obj in execution_order:
        file, app = obj
        file_path = f"{os.path.join(SEEDERS_PATH, file)}.seed.json"
        argv = [
            "python",
            "manage.py",
            "loaddata",
            file_path,
        ]

        subprocess.run(
            argv,
            shell=True,
            capture_output=False,
        )
        print(
            f"✅ Loaded {app.capitalize()} data from ./.seeds/{file}.seed.json to DATABASE"
        )


def database_seeding():
    argv_str = " ".join(sys.argv)

    if "--dumpdata" in argv_str or "-d" in argv_str:
        return dump_data_from_db()

    if "--loaddata" in argv_str or "-l" in argv_str:
        return load_data_from_db()

    sys.stdout.write("Please provide either --dumpdata or --loaddata as an argument")
    sys.stdout.write("Usage python manage.py seed  <-d | --dumpdata | -l | --loaddata>")


__all__ = ["database_seeding"]
