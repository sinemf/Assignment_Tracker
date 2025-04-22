import calendar
from django import template


register = template.Library()


@register.filter
def get_month_name(value):
   try:
       return calendar.month_name[int(value)]
   except:
       return value