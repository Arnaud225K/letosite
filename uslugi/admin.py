from django.contrib import admin
from django.utils.html import format_html
from .models import Uslugi
from utils.utils import get_admin_image_thumbnail_html


@admin.register(Uslugi)
class UslugiAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Uslugi.
    """
    list_display = ('name', 'display_service_image', 'description', 'is_hidden', 'created_at', 'updated_at',)
    # list_editable = ('is_hidden',)
    list_filter = ( 'is_hidden',)
    search_fields = ('name',)
    fieldsets = (
        (None, { 
            'fields': ('name', 'order_number', 'is_hidden', 'description', 'image',)
        }),
        ('Полное описание (Контент)', {
            'classes': ('collapse',),
            'fields': ('text',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at',)

    def display_service_image(self, obj):
        return get_admin_image_thumbnail_html(obj, image_field_name='image', alt_text_base="Услуга", width=50, height=50)
    display_service_image.short_description = 'Картинка'
