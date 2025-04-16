from django import template
import json
register = template.Library()

@register.filter
def get_value(dictionary, key):
    return dictionary.get(key, 0)

@register.filter
def to_json(value):
    """Converts a Python object to a JSON string."""
    return json.dumps(value)