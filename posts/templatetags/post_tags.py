from django import template

register = template.Library()

@register.filter
def format_date(value):
    return value.strftime('%d.%m.%Y %H:%M')