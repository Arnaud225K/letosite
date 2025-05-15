from django import forms
from menu.models import FilterCategory, FilterValue
from collections import defaultdict
import logging
logger = logging.getLogger(__name__)



class ProductFilterForm(forms.Form):
    """Valide les paramètres de filtre reçus via GET/AJAX."""
    # Pas de champ de tri ici pour l'instant

    def __init__(self, *args, **kwargs):
        available_filter_slugs = kwargs.pop('available_filter_slugs', [])
        super().__init__(*args, **kwargs)
        for slug in available_filter_slugs:
            self.fields[slug] = forms.MultipleChoiceField(choices=[], required=False)
        self.filter_field_names = available_filter_slugs

    def clean(self):
        cleaned_data = super().clean()
        active_filters = {}
        valid_value_slugs_by_cat = defaultdict(set)
        if self.filter_field_names:
            valid_values = FilterValue.objects.filter(
                category__slug__in=self.filter_field_names
            ).values('category__slug', 'slug')
            for item in valid_values:
                valid_value_slugs_by_cat[item['category__slug']].add(item['slug'])

        for cat_slug in self.filter_field_names:
            received_values = cleaned_data.get(cat_slug, [])
            if received_values:
                valid_received = []
                for val_slug in received_values:
                    if val_slug in valid_value_slugs_by_cat.get(cat_slug, set()):
                        valid_received.append(val_slug)
                    else: logger.warning(f"Invalid filter value '{val_slug}' for cat '{cat_slug}'.")
                if valid_received: active_filters[cat_slug] = valid_received

        cleaned_data['active_filters'] = active_filters
        return cleaned_data