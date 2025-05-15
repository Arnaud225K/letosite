from django.db import models

class SearchTerm(models.Model):
	q = models.CharField(max_length=512, verbose_name="Запрос пользователя")
	q_change = models.CharField(max_length=512, verbose_name="Искомая фраза", default='')
	search_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
	ip_address = models.GenericIPAddressField(verbose_name="IP пользователя")
	path_site = models.CharField(max_length=1024, verbose_name="Страница с которой искали", default='')
	filial_name = models.CharField(max_length=1024, verbose_name="Название города (по поддомену)", default='')
	subdomain_name = models.CharField(max_length=1024, verbose_name="Название поддомена", blank=True, null=True)
	tracking_id = models.CharField(max_length=50, default='', editable=False)
	
	def __str__(self):
		return self.q
	
	class Meta:
		ordering = ["-search_date"]
		verbose_name_plural = u"Поисковые запросы"


class SearchChange(models.Model):
	source = models.CharField(max_length=512, verbose_name="Исходное слово")
	result = models.CharField(max_length=512, verbose_name="Синоним")
	
	def __str__(self):
		return self.source + u' ' + self.result
	
	class Meta:
		verbose_name_plural = u"Таб. синонимов (замен)"


class SearchRemove(models.Model):
	str_remove = models.CharField(max_length=512, verbose_name="Исключаемое слово")
	
	def __str__(self):
		return self.str_remove
	
	class Meta:
		verbose_name_plural = u"Таб. исключений"
