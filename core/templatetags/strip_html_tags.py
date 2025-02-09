from django import template
from django.utils.html import strip_tags

register = template.Library()


@register.filter(name="strip_html")
def strip_html(value):
    """
    Removes HTML tags from the given text.
    """
    return strip_tags(value)
