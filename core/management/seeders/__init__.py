from core.management.seeders.categories import categories_seeding
from core.management.seeders.db_seed import database_seeding


def seeders():
    database_seeding()
    categories_seeding()
