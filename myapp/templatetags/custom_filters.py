# custom_filters.py

from django import template
import base64

register = template.Library()

@register.filter
def b64encode(image):
    if image:
        return base64.b64encode(image).decode('utf-8')
    return ''