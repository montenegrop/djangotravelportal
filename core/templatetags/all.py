from django import template

register = template.Library()

def addf(value, arg):
    """Adds the arg to the value."""
    return float(value) + float(arg)

addf.is_safe = False
register.filter(addf)
