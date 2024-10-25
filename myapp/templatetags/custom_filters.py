# custom_filters.py

from django import template
import base64

register = template.Library()

@register.filter
def b64encode(image_path):
    # Abre el archivo de imagen y lee su contenido como bytes
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()  # Leer la imagen como bytes
        return base64.b64encode(image_data).decode('utf-8')  # Codificar en base64