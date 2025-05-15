import os
from django import template

register = template.Library()

@register.filter(name='filename')
def filename(value):
    """
    Extrait le nom de fichier d'un chemin complet.
    Exemple: 'uploads/files/mon_fichier.pdf' -> 'mon_fichier.pdf'
    """
    if hasattr(value, 'name'):
        return os.path.basename(value.name)
    elif isinstance(value, str):
        return os.path.basename(value)
    return value