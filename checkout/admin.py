from django.contrib import admin
from .models import Order, OrderItem, Zakaz
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilterBuilder



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('product_title', 'price', 'quantity', 'get_item_cost_display',)
    readonly_fields = ('product_title', 'price', 'quantity', 'get_item_cost_display')
    extra = 0
    can_delete = False

    def get_item_cost_display(self, obj):
        """Affiche le coût formaté pour cet item dans l'inline."""
        if obj.pk:
            return f"{obj.get_cost()} ₽"
        return "-"
    get_item_cost_display.short_description = 'Стоимость'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_key', 'name', 'email', 'status', 'payment_method', 'paid', 'ip_address', 'display_total_cost', 'display_shipping_cost', 'display_grand_total', 'created_at')
    list_display_links = ('id', 'order_key')
    list_filter = ('status', 'payment_method', 'paid', 'created_at', 'type_client', 'shipping_method')
    search_fields = ('order_key', 'name', 'email', 'phone', 'ip_address')
    readonly_fields = ('order_key', 'created_at', 'updated_at', 'display_total_cost', 'display_shipping_cost', 'display_grand_total', 'total_paid', 'ip_address', 'file_display_link',)
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('order_key', ('status', 'payment_method', 'paid'), 'created_at', 'updated_at', 'display_total_cost', 'display_shipping_cost', 'display_grand_total', 'total_paid', 'transaction_id')
        }),
        ('Информация о клиенте', {
            'fields': ('name', 'email', 'phone', 'address', 'file_display_link', 'ip_address')
        }),
    )
    inlines = [OrderItemInline]
    # admin Actions
    actions = ['mark_as_paid', 'mark_as_shipped']


    # Méthodes d'affichage formatées
    def display_total_cost(self, obj):
        if obj.total_cost is not None:
            return format_html("<b>{} ₽</b>", obj.total_cost)
        return "-"
    display_total_cost.short_description = 'Стоимость товаров'

    def display_shipping_cost(self, obj):
        if obj.shipping_cost is not None:
            return format_html("{} ₽", obj.shipping_cost)
        return "0 ₽" # Ou "-"
    display_shipping_cost.short_description = 'Стоимость доставки'

    def display_grand_total(self, obj):
        if obj.grand_total_amount is not None:
            return format_html("<b>{} ₽</b>", obj.grand_total_amount)
        return "-"
    display_grand_total.short_description = 'Итоговая сумма заказа'
    display_grand_total.admin_order_field = 'grand_total_amount'


    def file_display_link(self, obj):
        """Méthode pour afficher un lien vers le fichier uploadé (si présent)"""
        if obj.file:
            # Return only the name of the paper
            return format_html('<a href="{}" target="_blank">{}</a>', obj.file.url, obj.file.name.split('/')[-1]) 
        return ("Файл не прикреплен")
    file_display_link.short_description = 'Прикрепленный файл'


    def mark_as_paid(self, request, queryset):
        """Logique pour marquer les commandes sélectionnées comme payées"""
        updated = queryset.update(paid=True, status=Order.STATUS_COMPLETED)
        self.message_user(request, f'{updated} заказов отмечены как оплаченные.')
    mark_as_paid.short_description = "Отметить выбранные заказы как оплаченные"

    def mark_as_shipped(self, request, queryset):
        """Logique pour marquer comme expédié"""
        updated = queryset.update(status=Order.STATUS_SHIPPED)
        self.message_user(request, f'{updated} заказов отмечены как отправленные.')
    mark_as_shipped.short_description = "Отметить выбранные заказы как отправленные"




class ZakazAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'date', 'type_order', 'ip_address', 'name', 'phone', 'email', 'text')
	list_filter = ('date',('date', DateRangeFilterBuilder()),)
	search_fields = ('type_order', 'email', 'name', 'id', 'phone', 'text')
	fieldsets = (
		('Info', {'fields': ('name', 'email', 'phone', 'text', 'ip_address',)}),
	)
admin.site.register(Zakaz, ZakazAdmin)
