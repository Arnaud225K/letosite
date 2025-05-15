from django.contrib import admin
from .models import Promo



@admin.register(Promo)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'order_number', 'is_show_main', 'is_hidden')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')