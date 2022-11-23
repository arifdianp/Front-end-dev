from django import template
register = template.Library()

@register.filter
def index(List, i):
    return List[int(i)]

@register.filter
def dicGet(Dict, key):
    if key is None:
        return False
    return Dict[key]

@register.filter
def lower(String):
    return String.lower()
