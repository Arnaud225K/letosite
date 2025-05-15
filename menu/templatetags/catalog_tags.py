from django import template
from django.template import Context, Template
import re
from menu.models import MenuCatalog 

register = template.Library()


def my_safe(value, current_filial):
	t = Template(value)
	c = Context({"current_filial": current_filial})
	text = t.render(c)
	return text
register.filter('my_safe', my_safe)


@register.filter(name='clean_html')
def clean_html(value):
    """
    Remove all HTML tags from the given string.
    """
    if isinstance(value, str):
        return re.sub(r'<.*?>', '', value)  # Remove all HTML tags
    return value

@register.filter(name='remove_space_href')
def remove_space_href(value):
    """
    Supprime les espaces, parenthèses et tirets d'une chaîne.
    Idéal pour formater un numéro de téléphone pour un lien 'tel:'.
    """
    if not isinstance(value, str):
        return value if value is not None else ""
    characters_to_remove = ['-', '(', ')', ' ']
    pattern = '[' + ''.join(re.escape(char) for char in characters_to_remove) + ']'
    cleaned_value = re.sub(pattern, '', value)
    return cleaned_value


@register.filter(name='format_price')
def format_price(value):
    if value is not None:
        return f"{value:,.0f}".replace(",", " ")
    return "0"



#TEMPLATE TAG MENU

@register.filter
def has_children(menu_item):
    """Checks if a MenuCatalog item has visible children."""
    if isinstance(menu_item, MenuCatalog):
        return menu_item.menucatalog_set.filter(is_hidden=False).exists()
    return False

@register.filter(name='range_to')
def range_to(start, end):
    """Generates a range from start up to and including end."""
    try:
        start = int(start)
        end = int(end)
        return range(start, end + 1)
    except (ValueError, TypeError):
        return []

@register.filter(name='make_list')
def make_list(value):
    """Converts an integer into a list for looping n times."""
    try:
        return range(1, int(value) + 1)
    except (ValueError, TypeError):
        return []