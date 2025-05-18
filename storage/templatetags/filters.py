# storage/templatetags/filters.py

from django import template

register = template.Library()

@register.filter
def filesizeformat(value):
    try:
        num_value = float(value)
    except (TypeError, ValueError):
        return "0.00 bytes"
        
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num_value < 1024.0:
            return f"{num_value:.2f} {unit}"
        num_value /= 1024.0
    return f"{num_value:.2f} PB"