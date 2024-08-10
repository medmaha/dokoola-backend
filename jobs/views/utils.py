
from core.models import Category
from django.db.models import Q

def get_category(slug:str):
    category = Category.objects.filter(Q(slug=slug)|Q(name=slug)).first()
    return category

