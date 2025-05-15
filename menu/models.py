import os
from django.db import models
from django.db.models.signals import post_delete, pre_save, post_save
from django_ckeditor_5.fields import CKEditor5Field
from transliterate import translit
from django.urls import reverse, NoReverseMatch
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import json
from unidecode import unidecode 
from django.utils import timezone
from django.utils.text import slugify
from django.core.files.storage import default_storage
import uuid
from django.db.models import Q, Case, When, IntegerField, Value, Count
from collections import defaultdict
from django.templatetags.static import static
import logging
logger = logging.getLogger(__name__)


def validate_image_size(image):
	# Validation de la taille de l'image (max 2MB)
	if image.size > 2 * 1024 * 1024:
		raise ValidationError("Размер изображения не должен превышать 2MB!")


class FeedLink(models.Model):
	feedlink = models.URLField(unique=True)
	etag = models.CharField(max_length=724, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Последняя проверка")
	enabled = models.BooleanField(default=True, help_text="Enable/disable periodic updates for this feed.")
	last_run_status = models.CharField("Статус последнего запуска", max_length=10, choices=[('success', 'Успех'), ('failure', 'Ошибка')], null=True, blank=True, editable=False, db_index=True)

	def __str__(self):
		return self.feedlink
	class Meta:
		verbose_name = "Ссылка на фид"
		verbose_name_plural = "Ссылки на фиды"



class FilterCategory(models.Model):
	""" Représente un type de filtre (ex: Fabricant, Couleur, Taille). """
	name = models.CharField("Название фильтра", max_length=100, unique=True)
	slug = models.SlugField("Ключ для URL", max_length=100, unique=True, help_text="Используется в URL (латиница, цифры, дефис)")
	ed_izm = models.CharField("Ед. измерения", max_length=128, blank=True, null=True)
	order = models.PositiveIntegerField("Порядок", default=100, help_text="Порядок отображения в списке фильтров")
	is_active = models.BooleanField("Активен", default=True, db_index=True)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Категория фильтра"
		verbose_name_plural = "Категории фильтров"
		ordering = ['order', 'name']

class FilterValue(models.Model):
	"""Représente une valeur possible pour un filtre (ex: Aquaviva, Rouge, XL)."""
	category = models.ForeignKey(FilterCategory, verbose_name="Категория фильтра", related_name='values', on_delete=models.CASCADE)
	value = models.CharField("Значение", max_length=255, db_index=True)
	slug = models.SlugField("Ключ для URL", max_length=255, blank=True, help_text="Генерируется автоматически, если пусто")
	order = models.PositiveIntegerField("Порядок", default=100)

	def __str__(self): return f"{self.category.name}: {self.value}"

	def save(self, *args, **kwargs):
		if not self.slug and self.value:
			self.slug = slugify(unidecode(self.value))[:255]
			base_slug = self.slug; counter = 1
			# Assure l'unicité du slug DANS la même catégorie de filtre
			while FilterValue.objects.filter(category=self.category, slug=self.slug).exclude(pk=self.pk).exists():
				self.slug = f"{base_slug}-{counter}"[:255]; counter += 1
				if counter > 50: self.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"[:255]; break
		super().save(*args, **kwargs)

	class Meta:
		verbose_name = "Значение фильтра"; verbose_name_plural = "Значения фильтров"
		ordering = ['category__order', 'category__name', 'order', 'value']
		unique_together = ('category', 'slug') # Garantit slug unique par catégorie
		indexes = [ models.Index(fields=['category', 'slug']) ]



class TypeMenu(models.Model):
	name = models.CharField(max_length=256, verbose_name="Название типа")
	template = models.CharField(max_length=724, verbose_name="Название файла шаблона")
	
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ["id"]
		verbose_name = "Тип меню"
		verbose_name_plural = "Типы меню"





class MenuCatalog(models.Model):
	order_number = models.FloatField(verbose_name="Порядок", blank=True, null=True)
	name = models.CharField(max_length=255, verbose_name="Название пункта", db_index=True)
	slug = models.SlugField(max_length=255, verbose_name="Название латинское", blank=True, unique=True, db_index=True)
	parent = models.ForeignKey("self", verbose_name="Родительский пункт", null=True, blank=True, on_delete=models.CASCADE, related_name='menucatalog_set', db_index=True)
	parents = models.ManyToManyField("self", verbose_name="Добавить подкатегории", db_table="MenuCatalog_and_parent_MenuCatalog", related_name="_id", blank=True, symmetrical=False)
	type_menu = models.ForeignKey(TypeMenu, verbose_name="Тип меню", related_name="type_menu", null=True, blank=True, on_delete=models.CASCADE, db_index=True)
	image = models.ImageField(upload_to='uploads/images', verbose_name="Картинка", blank=True, null=True, validators=[validate_image_size], help_text="Максимум 2MB")
	description = CKEditor5Field(config_name="extends", verbose_name="Описание", blank=True, null=True)
	flag_footer = models.BooleanField(verbose_name="Отображать в подвале", default=False)
	flag_main = models.BooleanField(verbose_name="Отображать на главной", default=False)
	title_main = models.CharField(max_length=512, verbose_name="Заголовок страницы", blank=True, null=True)
	keywords = models.TextField(verbose_name="Ключевые слова (мета)", blank=True, null=True, help_text="Ключевые слова для SEO продвижения (через запятую). Мета тэг - keywords")
	keywords_description = models.TextField(verbose_name="Описание (мета)", blank=True, null=True, help_text="Содержимое мета тэга - description")
	has_child = models.BooleanField(verbose_name="Есть вложенные категории", default=False, editable=False)
	is_hidden_child = models.BooleanField(verbose_name="Скрыть дочерние пункты", default=False)
	is_hidden = models.BooleanField(verbose_name='Скрыть', default=False)
	has_cover = models.BooleanField(verbose_name='С обложкой', default=False, help_text="Активируйте, если на странице есть обложка")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
	updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')


	def __str__(self):
		return self.name

	class Meta:
		ordering = ["-order_number"]
		verbose_name = "Меню/Каталог"
		verbose_name_plural = "Меню/Каталог"

		indexes = [
			# Index Parent + Type + Filtres + Ordre
			models.Index(
				fields=['parent', 'type_menu', 'is_hidden', 'order_number', 'name'],
				name='idx_menucat_sim_lookup'
			),
			# Index  catégories + type)
			models.Index(fields=['type_menu', 'is_hidden', 'order_number', 'name'], name='idx_menucat_toplevel'),
			# Index sur le slug
			models.Index(fields=['slug'], name='idx_menucat_slug'),
		]		
		

	def get_child(self):
		tmp = MenuCatalog.objects.filter(parent=self, is_hidden=False).exclude(id=2).only('name', 'slug', 'has_child')
		return tmp

	def get_childs(self):
		tmp = self.parents.all()
		return tmp

	def get_all_children(self):
		children = MenuCatalog.objects.filter(parent=self, is_hidden=False).only('id').exclude(id=2)
		return children

	def get_child_menu(self):
		child_menus = self.parents.filter(is_hidden=False).only('name', 'slug', 'has_child')
		child_menus |= MenuCatalog.objects.filter(parent=self, is_hidden=False).only('name', 'slug', 'has_child')
		return child_menus.distinct()


	# def get_absolute_url(self):
	# 	"""
	# 	Generates the hierarchical URL for this menu item.
	# 	"""
	# 	ancestors = self.get_ancestors(include_self=True)
	# 	#case if slug is null
	# 	slugs = [slugify(item.slug) if item.slug else '' for item in ancestors]
		
	# 	hierarchy = '/'.join(slugs)
	# 	return reverse('menu:menu_catalog', kwargs={'hierarchy': hierarchy})
		
	def get_absolute_url(self):
		ancestors = self.get_ancestors(include_self=True)
		slugs = [slugify(item.slug or f"cat-{item.id}") for item in ancestors]
		hierarchy = '/'.join(slugs)
		# --- Assurez-vous que 'menu:menu_catalog' est le nom du pattern SANS /f/ ---
		#    (celui avec juste <path:hierarchy>/)
		try:
			# Important: Utiliser le nom d'URL du pattern qui prend SEULEMENT la hiérarchie
			return reverse('menu:menu_catalog', kwargs={'hierarchy': hierarchy})
		except NoReverseMatch:
			logger.error(f"NoReverseMatch for 'menu:menu_catalog' with hierarchy: {hierarchy}")
			return f"/{hierarchy}/" # Fallback direct mais moins propre

	def get_ancestors(self, include_self=False):
		"""
		Helper method to get all ancestors (parents) of a menu item.
		"""
		ancestors = []
		current = self if include_self else self.parent
		while current:
			ancestors.insert(0, current)
			current = current.parent
		return ancestors

	def get_available_filters_data(self, base_product_queryset=None):
		"""
		Détermine les filtres et valeurs disponibles pour les produits
		associés à cette catégorie (ou un queryset fourni).
		Retourne un dictionnaire structuré optimisé pour le template.
		"""
		if base_product_queryset is None:
				# Si aucun queryset n'est fourni, prend tous les produits visibles/dispo de cette catégorie
				# Décidez si vous voulez inclure les sous-catégories ici
				categories_to_scan = [self]
				# Pour inclure les enfants:
				# descendants = self.get_descendants(include_self=True) # Si MPTT
				# categories_to_scan = list(descendants) if descendants else [self]
				base_product_queryset = Product.objects.filter(
					catalog__in=categories_to_scan,
					is_hidden=False,
				)

		# Récupère les FilterValues pertinentes AVEC le compte de produits DANS le queryset de base
		# et précharge la catégorie de filtre
		relevant_values_with_counts = FilterValue.objects.filter(
			products__in=base_product_queryset, # Liées aux produits de base
			category__is_active=True           # Catégorie de filtre active
		).select_related('category').annotate(
			# Compte les produits DANS le queryset de base pour cette valeur spécifique
			num_products=Count('products', filter=Q(products__in=base_product_queryset))
		).filter(num_products__gt=0).order_by( # Exclut si compte = 0
			'category__order', 'category__name', 'order', 'value'
		)

		# Structure les données pour le template
		available_filters = defaultdict(lambda: {'name': '', 'slug': '', 'values': []})
		for fv in relevant_values_with_counts:
			cat_slug = fv.category.slug
			# Initialise les infos catégorie si pas déjà fait
			if not available_filters[cat_slug]['name']:
					available_filters[cat_slug]['name'] = fv.category.name
					available_filters[cat_slug]['slug'] = cat_slug # Stocke le slug pour le name du checkbox

			# Ajoute les données de valeur
			available_filters[cat_slug]['values'].append({
				'name': fv.value,
				'slug': fv.slug,
				'count': fv.num_products,
				# 'is_active' sera déterminé dans le template/JS basé sur l'URL actuelle
			})

		# Convertir en dict normal ordonné par catégorie (si nécessaire)
		# Python 3.7+ maintient l'ordre d'insertion des clés pour dict
		return dict(available_filters)



class ProductImage(models.Model):
	product = models.ForeignKey('Product', related_name='additional_product_images', on_delete=models.CASCADE)
	image = models.ImageField("Изображение", upload_to='uploads/additional_images/')
	alt_text = models.CharField("Alt текст (для SEO)", max_length=255, blank=True, null=True)
	order = models.PositiveIntegerField("Порядок", default=0, help_text="Порядок отображения")
	is_custom_main = models.BooleanField(
		"Использовать как основное (заменяет из фида)",
		default=False,
		help_text="Если отмечено, это изображение будет показано как основное вместо изображения из фида."
	)
	uploaded_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['order', 'uploaded_at']
		verbose_name = "Доп. изображение продукта"
		verbose_name_plural = "Доп. изображения продуктов"

	def url(self):
		return self.image.url

	def name(self):
		return os.path.basename(self.image.url)

	def __str__(self):
		return f"Изображение для {self.product.title or self.product.sku} ({self.pk})"
		


class Product(models.Model):
	product_feed_id = models.CharField(max_length=100,  verbose_name="ID в фиде (может меняться)", db_index=True, blank=True, null=True)
	sku = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="Артикул (SKU)", help_text="Уникальный и стабильный идентификатор товара", blank=True, null=True)
	title = models.CharField(max_length=724, verbose_name="Название", db_index=True)
	slug = models.SlugField(max_length=724, verbose_name="Название латинское", blank=True, null=True)
	catalog = models.ForeignKey(MenuCatalog, verbose_name="Каталог", related_name='product_catalog_set', on_delete=models.CASCADE, db_index=True)
	description = CKEditor5Field(config_name="extends", verbose_name="Описание", blank=True, null=True)
	image = models.ImageField(max_length=724, upload_to='uploads/import_images/', null=True, blank=True, verbose_name="Картинка из фида")
	main_image = models.ImageField(
		"Картинка (локальная)", max_length=724, upload_to='uploads/images',
		null=True, blank=True, help_text="Загрузите сюда, если хотите переопределить изображение из фида."
		)	
	price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
	available = models.BooleanField(default=False, verbose_name="Доступность", db_index=True)
	availability_changed_at = models.DateTimeField("Доступность изменена", null=True, blank=True, db_index=True, editable=False)
	_original_available = None
	vendor = models.CharField(max_length=200, null=True, blank=True, verbose_name="Производитель")
	currencyId = models.CharField(max_length=10, null=True, blank=False, verbose_name='Валюта')
	store = models.BooleanField(default=False, null=False, blank=False, verbose_name='Доступно в магазине')
	delivery = models.BooleanField(default=False, null=False, blank=False, verbose_name='Доставка')
	pickup = models.BooleanField(default=False, null=False, blank=False, verbose_name='Самовывоз')
	created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='Создано')
	updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
	model = models.CharField(max_length=255, blank=True, null=True)
	ed_izm = models.CharField("Ед. измерения", max_length=50, blank=True, null=True, help_text="Единица измерения (напр., шт, кг, м², м³)")
	filters = models.ManyToManyField(FilterValue, verbose_name="Фильтры продукта", related_name='products', blank=True)
	additional_images = models.JSONField(blank=True, null=True, verbose_name="Доп. Картинки")
	params = models.JSONField(blank=True, null=True, verbose_name='Параметры')
	title_main = models.CharField(max_length=512, verbose_name="Заголовок страницы", blank=True, null=True)
	keywords = models.TextField(verbose_name="Ключевые слова (мета)", blank=True, null=True)
	keywords_description = models.TextField(verbose_name="Описание (мета)", blank=True, null=True)
	is_hidden = models.BooleanField(verbose_name="Скрыть", default=False)
	is_hit = models.BooleanField(verbose_name="Xит", default=False, help_text="Показать на главной для хиты", db_index=True)
	country_of_origin = models.CharField("Страна производства", max_length=255, blank=True, null=True)
	manufacturer_override = models.CharField("Производитель (если отличается от Vendor)", max_length=255, blank=True, null=True, help_text="Используйте, если 'Производитель' из фида неточен")
	form_of_release = models.CharField("Форма выпуска", max_length=255, blank=True, null=True)
	warranty_info = models.TextField("Гарантия", blank=True, null=True)
	additional_details = models.TextField("Дополнительно (детали)", blank=True, null=True, help_text="Текстовый блок для дополнительной информации.")
	delivery_terms_override = models.TextField("Условия доставки (специфичные для товара)", blank=True, null=True, help_text="Если отличаются от общих условий.")
	downloadable_materials_info = models.TextField("Скачиваемые материалы", blank=True, null=True)

	#Stores 'available' status at time object is loaded from DB or created
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._original_available = self.available

	# Determines whether to update availability_changed_at
	def save(self, *args, **kwargs):
		update_change_timestamp = False
		if self.pk is not None:
			if self.available != self._original_available:
				update_change_timestamp = True
		else:
				update_change_timestamp = True

		if update_change_timestamp:
			self.availability_changed_at = timezone.now()

		super().save(*args, **kwargs)
		self._original_available = self.available

	def __str__(self):
		return self.title

	class Meta:
		ordering = ["catalog", "title"]
		verbose_name = "Продукт"
		verbose_name_plural = "Продукты"
		indexes = [
		# Index explicite sur SKU
		models.Index(fields=['sku'], name='idx_product_sku'),
		#Index pour le filtre principal (catégorie + critères communs + tri)
		models.Index(fields=['catalog', 'is_hidden', '-created_at'], name='idx_prod_cat_criteria_ord'), 
		# Index pour la requête de la page d'accueil
		models.Index(fields=['is_hit', 'is_hidden', 'available', '-created_at'], name='idx_prod_hit_main'),
		# Index pour la tâche de notification
		models.Index(fields=['availability_changed_at'], name='idx_prod_avail_changed'),
		models.Index(fields=['catalog', 'available', 'availability_changed_at'], name='idx_prod_cat_avail_chng'),
		]
	
	def get_absolute_url(self):
		return reverse('menu:product', kwargs={'product_slug': self.slug})

	def generate_url(self):
		return '/product/' + self.slug + '/'


	def update_filter_values(self, param_dict):
			values_to_set = []; active_cats = {fc.slug: fc for fc in FilterCategory.objects.filter(is_active=True)}
			for filter_cat_slug, value_str in param_dict.items():
				if not value_str: continue; filter_cat = active_cats.get(filter_cat_slug)
				if filter_cat:
					vals = [v.strip() for v in str(value_str).split('|') if v.strip()]
					for val in vals: fv, cr = FilterValue.objects.get_or_create(category=filter_cat, value=val); values_to_set.append(fv)
			if values_to_set: self.filters.set(values_to_set); logger.debug(f"Set filters P:{self.sku}")
			elif self.filters.exists(): self.filters.clear(); logger.debug(f"Clear filters P:{self.sku}")

	def get_main_image_url(self):
		"""
		Retourne l'URL de l'image principale à afficher.
		Priorité : Image personnalisée marquée comme principale, puis image locale,
		puis image du flux, puis image par défaut.
		"""
		# 1. Cherche une image supplémentaire marquée comme principale
		# custom_main_image = self.additional_product_images.filter(is_custom_main=True).first()
		# if custom_main_image and custom_main_image.image and hasattr(custom_main_image.image, 'url'):
		# 	try: return custom_main_image.image.url
		# 	except ValueError: logger.warning(f"P {self.pk}: Custom main ProductImage file missing.")

		# 2. Utilise le champ 'image' (local/uploadé manuellement)
		if self.main_image and hasattr(self.main_image, 'url'):
			try: return self.main_image.url
			except ValueError: logger.warning(f"P {self.pk}: Main local 'image' file missing.")

		# 3. Utilise l'image du flux si disponible
		if self.image and hasattr(self.image, 'url'):
			try: return self.image.url
			except ValueError: logger.warning(f"P {self.pk}: Feed 'image' file missing.")




class AvailabilityReport(models.Model):
	"""Enregistre les informations sur les rapports de disponibilité générés."""
	STATUS_PENDING = 'pending'
	STATUS_GENERATED = 'generated'
	STATUS_NOTIFIED = 'notified'
	STATUS_FAILED = 'failed'
	STATUS_CHOICES = [
		(STATUS_PENDING, 'В ожидании'),
		(STATUS_GENERATED, 'Сгенерирован (файл)'),
		(STATUS_NOTIFIED, 'Уведомление отправлено'),
		(STATUS_FAILED, 'Ошибка'),
	]
	REPORT_TYPE_AVAILABILITY_CHANGE = 'availability_change'
	REPORT_TYPES = [
		(REPORT_TYPE_AVAILABILITY_CHANGE, 'Изменения доступности'),
	]

	report_type = models.CharField("Тип отчета", max_length=50, choices=REPORT_TYPES, default=REPORT_TYPE_AVAILABILITY_CHANGE)
	status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
	generated_at = models.DateTimeField("Дата генерации", default=timezone.now, editable=False)
	file_path = models.CharField("Путь к файлу", max_length=512, editable=False)
	filename = models.CharField("Имя файла", max_length=255, editable=False)
	product_change_count = models.PositiveIntegerField("Всего измененных продуктов", default=0, editable=False)
	unavailable_count = models.PositiveIntegerField("Стали недоступны (шт.)", default=0, editable=False)
	available_count = models.PositiveIntegerField("Стали доступны (шт.)", default=0, editable=False)
	error_message = models.TextField("Сообщение об ошибке", blank=True, null=True, editable=False)
	notified_products = models.ManyToManyField(Product, related_name='availability_reports', editable=False, blank=True)

	class Meta:
		ordering = ['-generated_at']
		verbose_name = "Отчет о доступности"
		verbose_name_plural = "Отчеты о доступности"

	def __str__(self):
		return f"Отчет ({self.get_report_type_display()}) - {self.generated_at.strftime('%Y-%m-%d %H:%M')}"

	def get_download_url(self):
		"""Tente de retourner l'URL publique du fichier."""
		from django.core.files.storage import default_storage
		try:
			return default_storage.url(self.file_path)
		except NotImplementedError:
			return None
		except Exception as e:
			# Log l'erreur
			print(f"Error getting URL for report {self.id}: {e}")
			return None

	def display_download_link(self):
		"""Affiche un lien téléchargeable dans l'admin."""
		url = self.get_download_url()
		if url:
			from django.utils.html import format_html
			return format_html('<a href="{}" download>Скачать {}</a>', url, self.filename)
		return "Ссылка недоступна"
	display_download_link.short_description = "Скачать отчет"


def delete_report_file_on_report_delete(sender, instance, **kwargs):
	"""
	Supprime le fichier physique associé lorsqu'un objet AvailabilityReport est supprimé.
	"""
	if instance.file_path:
		if default_storage.exists(instance.file_path):
			try:
				default_storage.delete(instance.file_path)
			except Exception as e:
				logger.error(f"Error deleting report file {instance.file_path} for {sender.__name__} ID: {instance.pk}: {e}", exc_info=True)
		else:
			logger.warning(f"Report file not found in storage: {instance.file_path} for {sender.__name__} ID: {instance.pk}")
post_delete.connect(delete_report_file_on_report_delete, sender=AvailabilityReport)

