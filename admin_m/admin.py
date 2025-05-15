# from django.urls import path
# from django.contrib import admin
# from promo.models import Promo
# from admin_m.views import ProductExportSetupView

# class PromoProxy(Promo):
#     class Meta:
#         proxy = True
#         verbose_name = "Настройка экспорта товаров"
#         verbose_name_plural = "Настройка экспорта товаров"

# class PromoProxyAdmin(admin.ModelAdmin):
#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path(
#                 'product-export/',
#                 self.admin_site.admin_view(ProductExportSetupView.as_view()),
#                 name='product_export_setup',
#             ),
#         ]
#         return custom_urls + urls

# admin.site.register(PromoProxy, PromoProxyAdmin)