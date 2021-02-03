from django import template
import calendar

register = template.Library()

@register.filter
def month_name(value):
    return calendar.month_name[value]

@register.filter
def string_trunc(content, length=300, suffix='...'):
    if len(content) > length:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix   
    return content