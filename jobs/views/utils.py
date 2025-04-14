from django.db.models import Q

from core.models import Category


def get_category(slug: str):
    _slug = slug.lower() if slug else None
    category = Category.objects.filter(
        Q(slug__iexact=_slug) | Q(name__iexact=_slug)
    ).first()
    return category
