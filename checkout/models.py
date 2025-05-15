from django.db import models
from menu.models import Product
from decimal import Decimal
import uuid

class Order(models.Model):
	STATUS_PENDING = 'pending'
	STATUS_PROCESSING = 'processing'
	STATUS_SHIPPED = 'shipped'
	STATUS_DELIVERED = 'delivered'
	STATUS_PAID_ON_DELIVERY = 'paid_on_delivery'
	STATUS_PAID_CASH = 'paid_cash'
	STATUS_COMPLETED = 'completed'
	STATUS_CANCELLED = 'cancelled'
	STATUS_PENDING_PAYMENT = 'pending_payment'
	STATUS_PAYMENT_FAILED = 'payment_failed'

	ORDER_STATUS_CHOICES = [
		(STATUS_PENDING, 'В ожидании'),
		(STATUS_PENDING_PAYMENT, 'Ожидание онлайн-оплаты'),
		(STATUS_PROCESSING, 'В обработке'),
		(STATUS_SHIPPED, 'Отправлено'),
		(STATUS_DELIVERED, 'Доставлено'),
		(STATUS_PAID_ON_DELIVERY, 'Оплачено при доставке'),
		(STATUS_PAID_CASH, 'Оплачено наличными'),
		(STATUS_PAYMENT_FAILED, 'Ошибка онлайн-оплаты'),
		(STATUS_COMPLETED, 'Завершено'),
		(STATUS_CANCELLED, 'Отменено'),
	]

	PAYMENT_ON_DELIVERY = 'on_delivery'
	PAYMENT_CASH = 'cash'
	PAYMENT_ONLINE_YOOKASSA = 'online_yookassa'
	PAYMENT_GET_OFFER = 'get_offer'

	PAYMENT_METHOD_CHOICES = [
		(PAYMENT_GET_OFFER, 'Получить коммерческое предложение'),
		(PAYMENT_ONLINE_YOOKASSA, 'Картой онлайн (Скидка 4%)'),
		(PAYMENT_ON_DELIVERY, 'Наличными либо картой'),
		(PAYMENT_CASH, 'Безналичной оплатой'),
	]

	# --- CLIENT TYPE ---
	TYPE_INDIVIDUAL = 'individual'
	TYPE_LEGAL_ENTITY = 'legal_entity'
	CLIENT_TYPE_CHOICES = [
		(TYPE_INDIVIDUAL, 'Физическое лицо'),
		(TYPE_LEGAL_ENTITY, 'Юридическое лицо'),
	]

	# --- DELIVERY ---
	DELIVERY_MKAD_INSIDE = 'mkad_inside'
	DELIVERY_MKAD_OUTSIDE = 'mkad_outside'
	DELIVERY_RUSSIA = 'russia'

	DELIVERY_CHOICES = [
		(DELIVERY_MKAD_INSIDE, 'В пределах МКАД'),
		(DELIVERY_MKAD_OUTSIDE, 'За пределы МКАД'),
		(DELIVERY_RUSSIA, 'по России в пункт выдачи'),
	]

	name = models.CharField("Ф.И.О", max_length=100, blank=True, default='')
	email = models.EmailField("E-mail", max_length=254)
	phone = models.CharField("Телефон", max_length=20)
	address = models.CharField("Адрес доставки", max_length=255, null=True, blank=True)
	ip_address = models.GenericIPAddressField("IP адрес", null=True, blank=True)
	last_updated = models.DateTimeField(auto_now=True)
	type_order = models.CharField(verbose_name="Тип", max_length=128, default='')
	type_client = models.CharField("Тип клиента",max_length=20, choices=CLIENT_TYPE_CHOICES, default=TYPE_INDIVIDUAL)
	file = models.FileField( upload_to='uploads/files', verbose_name="Прикрепить файл (реквизиты)", blank=True, null=True, help_text="Например, реквизиты для юридических лиц")
	created_at = models.DateTimeField("Создано", auto_now_add=True)
	updated_at = models.DateTimeField("Обновлено", auto_now=True)
	status = models.CharField("Статус", max_length=20, choices=ORDER_STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
	payment_method = models.CharField("Способ оплаты", max_length=20, choices=PAYMENT_METHOD_CHOICES)
	paid = models.BooleanField("Оплачено", default=False, db_index=True)
	total_cost = models.DecimalField("Общая стоимость заказа", max_digits=12, decimal_places=0, default=Decimal(0))
	shipping_cost = models.DecimalField("Стоимость доставки", max_digits=12, decimal_places=0, default=Decimal(0))
	grand_total_amount = models.DecimalField("Итоговая сумма заказа (сохранено)", max_digits=12, decimal_places=0, default=Decimal('0'))
	total_paid = models.DecimalField("Оплаченная сумма", max_digits=12, decimal_places=0, default=Decimal(0))
	order_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
	transaction_id = models.CharField("ID транзакции", max_length=255, blank=True, null=True, db_index=True)
	shipping_method = models.CharField("Способ доставки", max_length=20, choices=DELIVERY_CHOICES, null=True, blank=True)
	shipping_distance_km = models.PositiveIntegerField("Расстояние за МКАД (км)", null=True, blank=True, help_text="Укажите расстояние в км, если доставка за МКАД")
	yookassa_payment_id = models.CharField("ID платежа YooKassa", max_length=50, blank=True, null=True, unique=True, db_index=True)
	yookassa_payment_status = models.CharField("Статус платежа YooKassa", max_length=30, blank=True, null=True) #pending, succeeded, canceled

	class Meta:
		ordering = ('-created_at',)
		verbose_name = "Заказ"
		verbose_name_plural = "Заказы"

	def __str__(self):
		return f"Заказ {self.id} ({self.order_key})"

	def get_total_cost(self):
		"""Calcule le coût total basé sur les articles enregistrés."""
		total = self.items.aggregate(
			total_cost=models.Sum(models.F('price') * models.F('quantity'), output_field=models.DecimalField(max_digits=12, decimal_places=0))
		)['total_cost']
		return total or Decimal('0')

	def calculate_grand_total(self):
		return (self.total_cost or Decimal('0')) + (self.shipping_cost or Decimal('0'))
	
	def get_grand_total(self):
		"""Calcule le coût total de la commande (Articles + Livraison)."""
		shipping = self.shipping_cost if self.shipping_cost is not None else Decimal('0')
		items_total = self.total_cost if self.total_cost is not None else Decimal('0')
		return items_total + shipping

class OrderItem(models.Model):
	order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name='order_items', on_delete=models.SET_NULL, null=True, blank=True)
	product_title = models.CharField("Название товара", max_length=724)
	price = models.DecimalField("Цена за единицу", max_digits=12, decimal_places=0)
	quantity = models.PositiveIntegerField("Количество", default=1)

	class Meta:
		ordering = ('pk',)
		verbose_name = "Позиция заказа"
		verbose_name_plural = "Позиции заказа"

	def __str__(self):
		return str(self.id)

	def get_cost(self):
		"""Calcule le coût de cette ligne d'article."""
		return self.price * Decimal(self.quantity)
	



class Zakaz(models.Model):
	name = models.CharField(verbose_name="Ф.И.О", max_length=50)
	email = models.EmailField(verbose_name="E-mail", max_length=50, blank=True, null=True, default='')
	phone = models.CharField(verbose_name="Телефон", max_length=20)
	date = models.DateTimeField(auto_now_add=True)
	ip_address = models.GenericIPAddressField()
	last_updated = models.DateTimeField(auto_now=True)
	type_order = models.CharField(verbose_name="Тип", max_length=128, default='')
	type_client = models.CharField(verbose_name="Клиент", max_length=128, default='')
	text = models.TextField(verbose_name="Текст", blank=True, null=True)
	email_to = models.EmailField(verbose_name="Отправлен", max_length=50, default="", blank=True, null=True)
	
	class Meta:
		ordering = ["-date",]
		verbose_name = "Заявки"
		verbose_name_plural = "Заявки"
	
	def __str__(self):
		return 'Заказ #' + str(self.id)