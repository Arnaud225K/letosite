# import urllib3
from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect
from django import forms
from .models import MenuCatalog, TypeMenu, Product , FeedLink, AvailabilityReport, FilterCategory, FilterValue, ProductImage
# from .parser import parse_data, fetch_yml_data
from django.db import IntegrityError
from .tasks import update_feed_data
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from utils.utils import get_admin_image_thumbnail_html
import logging



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('feed_processing.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


ID_UNCATEGORIZED_CATEGORY = '2'
ID_TYPE_CATEGORY_LIST = 7
ID_TYPE_CATEGORY_LIST_2 =8
# ID_TYPE_CATEGORY =6

class UncategorizedProductFilter(admin.SimpleListFilter):
	title = 'Статус категории'
	parameter_name = 'category_status'

	def lookups(self, request, model_admin):
		return (
			('uncategorized', 'Неразнесенные товары'),
			('categorized', 'Разнесенные товары'),
		)

	def queryset(self, request, queryset):
		uncategorized_category_id = ID_UNCATEGORIZED_CATEGORY
		if self.value() == 'uncategorized':
			return queryset.filter(catalog__id=uncategorized_category_id)
		elif self.value() == 'categorized':
			return queryset.exclude(catalog__id=uncategorized_category_id)
		return queryset

# --- Custom Form for Bulk Category Assignment ---
class AssignCategoryForm(forms.Form):
	_selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
	category = forms.ModelChoiceField(
		queryset=MenuCatalog.objects.none(),
		label="Выберите категорию"
	)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['category'].queryset = MenuCatalog.objects.filter(
			type_menu_id__in=[ID_TYPE_CATEGORY_LIST, ID_TYPE_CATEGORY_LIST_2]
		).exclude(
			id=ID_UNCATEGORIZED_CATEGORY
		).order_by('name')


class CategoryFilter(admin.SimpleListFilter):
	"""
	A custom filter to allow selecting a specific category (excluding uncategorized).
	"""
	title = 'Категория'
	parameter_name = 'category_id'

	def lookups(self, request, model_admin):
		# All categories with product except the uncategorized
		categories = MenuCatalog.objects.filter(type_menu_id__in=[
					ID_TYPE_CATEGORY_LIST,ID_TYPE_CATEGORY_LIST_2]).exclude(
					id=ID_UNCATEGORIZED_CATEGORY).order_by('name')
		
		return [(category.id, category.name) for category in categories]

	def queryset(self, request, queryset):
		if self.value():
			return queryset.filter(catalog__id=self.value())
		return queryset



class MenuCatalogAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug': ('name',)}
	list_display = ('id', 'name', 'display_catalog_image', 'slug', 'order_number', 'parent', 'type_menu', 'is_hidden', 'created_at', 'updated_at')
	list_display_links = ('id', 'name')

	search_fields = ('name', 'slug')
	list_filter = ('type_menu', 'is_hidden', 'parent')
	prepopulated_fields = {'slug': ('name',)}

	readonly_fields = ('has_child','created_at','updated_at',)

	fieldsets = (
		(None, {
			'fields': (
				'order_number',
				'name',
				'slug',
				'parent',
				'type_menu',
				'image',
				'description',
			)
		}),
		('Связанные подкатегории (M2M)', {
			'classes': ('collapse',),
			'fields': ('parents',)
		}),
		('Настройки отображения', {
			'classes': ('collapse',),
			'fields': (
				'is_hidden',
				'is_hidden_child',
				'has_cover',
				'flag_footer',
				'flag_main',
			)
		}),
		('SEO и Заголовки', {
			'classes': ('collapse',),
			'fields': (
				'title_main',
				'keywords',
				'keywords_description',
			)
		}),
		('Информация', {
			'classes': ('collapse',),
			'fields': ('has_child', 'created_at', 'updated_at')
		}),
	)

	def display_catalog_image(self, obj):
		return get_admin_image_thumbnail_html(obj, image_field_name='image', alt_text_base="Категория")
	display_catalog_image.short_description = 'Картинка'


admin.site.register(MenuCatalog, MenuCatalogAdmin)




class ProductImageInline(admin.TabularInline):
	model = ProductImage
	fields = ('image', 'display_thumbnail_admin', 'alt_text', 'order', 'is_custom_main')
	readonly_fields = ('display_thumbnail_admin',)
	extra = 1
	verbose_name = "Доп. изображение"
	verbose_name_plural = "Доп. изображения"
	fk_name = 'product'
	
	def display_thumbnail_admin(self, obj):
		return get_admin_image_thumbnail_html(obj, image_field_name='image', alt_text_base="Доп. продукт")
	display_thumbnail_admin.short_description = 'Доп. Картинка'


class ProductCatalogAdmin(admin.ModelAdmin):

	prepopulated_fields = {'slug': ('title',)}
	list_display = ('id', 'sku', 'title', 'display_product_image', 'slug', 'catalog', 'available', 'is_hidden', 'is_hit', 'created_at', 'updated_at')
	list_display_links = ('id', 'title')
	search_fields = ('title', 'slug', 'id', 'sku', 'catalog__name')
	list_select_related = ('catalog',)
	list_filter = (UncategorizedProductFilter, CategoryFilter, 'available', 'is_hidden', 'is_hit',)
	readonly_fields = ('id','created_at', 'updated_at',)
	actions = ['assign_category',]
	filter_horizontal = ('filters',)


	inlines = [ProductImageInline]

	fieldsets = (
		('Основное', {'fields': ('sku', 'title', 'slug', 'catalog', 'price', 'currencyId', 'ed_izm', 'vendor', 'model')}),
		('Статус', {'fields': ('available', 'is_hidden', 'is_hit',)}),
		('Изображения', {'fields': ('image', 'main_image', 'additional_images')}),
		('Детали Продукта', {
			'classes': ('collapse',),
			'fields': (
				'country_of_origin',
				'manufacturer_override',
				'form_of_release',
				'warranty_info',
				'additional_details',
				'delivery_terms_override',
				'downloadable_materials_info',
			)
		}),		
		('Описание и SEO', {'classes': ('collapse',), 'fields': ('description', 'title_main', 'keywords', 'keywords_description')}),
		('Назначенные фильтры', {'classes': ('',), 'fields': ('filters',)}),
		('Доп.', {'classes': ('collapse',), 'fields': ('params','created_at', 'updated_at', 'product_feed_id',)}),
	)

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "catalog":
			kwargs["queryset"] = MenuCatalog.objects.filter(
					type_menu_id__in=[ID_TYPE_CATEGORY_LIST, ID_TYPE_CATEGORY_LIST_2]
			).exclude(
				id=ID_UNCATEGORIZED_CATEGORY
			).order_by('name')
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

	def assign_category(self, request, queryset):
		"""
		Custom admin action to assign selected products to a chosen category.
		"""
		form = None

		if 'apply' in request.POST:
			form = AssignCategoryForm(request.POST)

			if form.is_valid():
				category = form.cleaned_data['category']
				selected_products = request.POST.getlist('_selected_action')

				Product.objects.filter(pk__in=selected_products).update(catalog=category)

				self.message_user(request, f"Успешно назначено {len(selected_products)} товаров на категорию: {category.name}")
				return redirect(request.get_full_path()) 

		if not form:
			form = AssignCategoryForm(initial={'_selected_action': request.POST.getlist(admin.helpers.ACTION_CHECKBOX_NAME)})

		return render(request, 'admin/assign_category.html', {'products': queryset, 'category_form': form})

	assign_category.short_description = "Назначить выбранные Продукт к категории"


	def get_urls(self):
		urls = super().get_urls()
		my_urls = [
			path('assign-category/', self.assign_category, name='assign_category'),
		]
		return my_urls + urls

	def display_product_image(self, obj):
		return get_admin_image_thumbnail_html(obj, image_field_name='image', alt_text_base="Продукт")
	display_product_image.short_description = 'Картинка'


	@admin.action(description='Назначить категорию выбранным продуктам')
	def assign_category_action(self, request, queryset):
		form = None
		if 'apply' in request.POST:
			form = AssignCategoryForm(request.POST)
			if form.is_valid():
				category = form.cleaned_data['category']
				selected_pks = request.POST.getlist(admin.helpers.ACTION_CHECKBOX_NAME)
				updated_count = queryset.filter(pk__in=selected_pks).update(catalog=category)
				self.message_user(request, f"Успешно назначено {updated_count} продуктов на категорию: {category.name}", messages.SUCCESS)
				return None
		else:
			form = AssignCategoryForm(initial={'_selected_action': queryset.values_list('pk', flat=True)})

		context = { **self.admin_site.each_context(request), 'title': 'Назначить категорию',
					'queryset': queryset, 'opts': self.model._meta, 'category_form': form,
					'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME }
		return render(request, 'admin/assign_category_intermediate.html', context)

admin.site.register(Product, ProductCatalogAdmin)


class FeedLinkAdmin(admin.ModelAdmin):
	list_display = ('feedlink', 'etag', 'enabled', 'created_at', 'updated_at', 'last_run_status')
	fields = ['feedlink', 'enabled']
	list_filter = ('enabled',) 
	search_fields = ('feedlink',)

	def save_model(self, request, obj, form, change):
		if 'feedlink' in form.changed_data or 'enabled' in form.changed_data or not change:
			try:
				super().save_model(request, obj, form, change)
			except IntegrityError:
				logger.error(f"Ссылка уже существует: {obj.feedlink}")
				messages.error(request, f"FeedLink уже существует: {obj.feedlink}")
				return

			if 'feedlink' in form.changed_data or not change:
				update_feed_data.delay(obj.feedlink)
		else:
			super().save_model(request, obj, form, change)

admin.site.register(FeedLink, FeedLinkAdmin)



@admin.register(AvailabilityReport)
class AvailabilityReportAdmin(admin.ModelAdmin):
	list_display = (
		'generated_at',         
		'report_type_display',  
		'status_display',       
		'product_change_count',
		'available_count',
		'unavailable_count',
		'display_download_link',
		'filename',
	)
	def report_type_display(self, obj): return obj.get_report_type_display()
	report_type_display.short_description = 'Тип отчета'
	report_type_display.admin_order_field = 'report_type'

	def status_display(self, obj): return obj.get_status_display()
	status_display.short_description = 'Статус'
	status_display.admin_order_field = 'status'

	list_filter = (
		'status',            
		'report_type',
		'generated_at',
	)

	search_fields = (
		'filename',
		'error_message',
	)

	date_hierarchy = 'generated_at'

	readonly_fields = (
		'report_type',
		'status',
		'generated_at',
		'file_path',
		'filename',
		'display_download_link_detail',
		'product_change_count',
		'unavailable_count',
		'available_count',
		'error_message',
		'display_notified_products_link', 
	)
	exclude = ('notified_products',)

	fieldsets = (
		('Основная информация', {
			'fields': ('report_type', 'status', 'generated_at', 'error_message')
		}),
		('Содержимое отчета', {
			'fields': ('product_change_count', 'available_count', 'unavailable_count', 'filename', 'display_download_link_detail')
		}),
		('Связанные продукты', {
			'fields': ('display_notified_products_link',)
		}),
	)

	def display_download_link_detail(self, obj):
		"""Affiche le lien de téléchargement dans la vue détail."""
		return obj.display_download_link()
	display_download_link_detail.short_description = "Ссылка на скачивание"

	def display_notified_products_link(self, obj):
		"""Affiche un lien vers la liste filtrée des produits notifiés."""
		count = obj.notified_products.count()
		if count == 0:
			return "Нет связанных продуктов"

		url = (
			reverse("admin:menu_product_changelist")
			+ "?"
			+ urlencode({"id__in": f"{','.join(str(p.pk) for p in obj.notified_products.all())}"})
		)
		return format_html('<a href="{}">Посмотреть {} продуктов</a>', url, count)
	display_notified_products_link.short_description = "Продукты в этом отчете"


	def has_add_permission(self, request):
		return True

	def has_change_permission(self, request, obj=None):
		return True

	def has_delete_permission(self, request, obj=None):
		return True




# --- Enregistrement des autres modèles ---
@admin.register(FilterCategory)
class FilterCategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', 'order', 'is_active')
	list_editable = ('order', 'is_active')
	search_fields = ('name',)
	prepopulated_fields = {'slug': ('name',)}

@admin.register(FilterValue)
class FilterValueAdmin(admin.ModelAdmin):
	list_display = ('value', 'category', 'slug', 'order')
	list_filter = ('category',)
	search_fields = ('value', 'category__name')
	list_editable = ('order',)
	list_select_related = ('category',)
	autocomplete_fields = ['category']
	def get_readonly_fields(self, request, obj=None):
		if obj: return self.readonly_fields + ('slug',)
		return self.readonly_fields

admin.site.register(TypeMenu)
