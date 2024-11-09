# storage/templatetags/filters.py

from django import template

register = template.Library()

@register.filter
def filesizeformat(value):
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if value < 1024.0:
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{value:.2f} PB"
