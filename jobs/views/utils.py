from django.db.models import Q

from core.models import Category


def get_category(slug: str):
    category = Category.objects.filter(Q(slug=slug) | Q(name=slug)).first()
    return category
