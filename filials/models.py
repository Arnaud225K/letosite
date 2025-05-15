from django.db import models

class Filials(models.Model):
    order_number = models.FloatField(verbose_name="Порядковый номер", blank=True, null=True)
    name = models.CharField(max_length=100, verbose_name="Название")
    name_info = models.CharField(max_length=100, verbose_name="Название (падеж для подстановки)", blank=True, null=True)
    region = models.CharField(max_length=100, verbose_name="Область", blank=True, null=True)
    subdomain_name = models.CharField(max_length=100, verbose_name="Название поддомена")
    filials_name = models.ForeignKey('self', verbose_name="Основной филиал", on_delete=models.CASCADE, blank=True, null=True)
    phone = models.CharField(max_length=50, verbose_name="Телефон", blank=True, null=True)
    email = models.CharField(max_length=50, verbose_name="Электронная почта", blank=True, null=True)
    phone_dop = models.CharField(max_length=50, verbose_name="Телефон (дополнительный)", blank=True, null=True)
    address = models.CharField(max_length=256, verbose_name="Адрес", blank=True, null=True)
    rezhim = models.CharField(max_length=1024, verbose_name="Режим работы", blank=True, null=True)
    comment = models.TextField(verbose_name="Карта проезда", blank=True, null=True)
    robots = models.TextField(verbose_name="Общий robots.txt", blank=True, null=True)
    sitemap_name = models.CharField(max_length=1024, verbose_name="Имя карты сайта", blank=True, null=True)
    req_file = models.FileField(upload_to='uploads/files', verbose_name="Реквизиты (файл)", blank=True, null=True)
    sertificate = models.CharField(max_length=1024, verbose_name="Сертификат", blank=True, null=True)
    text_head_filial = models.TextField(verbose_name="Блок в head для филиала (внизу)", blank=True, null=True)
    text_body_filial = models.TextField(verbose_name="Блок в body для филиала (внизу)", blank=True, null=True)

    full_name_req = models.CharField(max_length=256, verbose_name="Полное наименование предприятия", blank=True, null=True)
    short_name_req = models.CharField(max_length=256, verbose_name="Краткое наименование предприятия", blank=True, null=True)
    inn_req = models.CharField(max_length=100, verbose_name="ИНН", blank=True, null=True)
    kpp_req = models.CharField(max_length=100, verbose_name="КПП", blank=True, null=True)
    bin_req = models.CharField(max_length=100, verbose_name="БИН (КЗ)", blank=True, null=True)
    ikk_1_req = models.CharField(max_length=100, verbose_name="ИКК 1 (КЗ)", blank=True, null=True)
    ikk_2_req = models.CharField(max_length=100, verbose_name="ИКК 2 (КЗ)", blank=True, null=True)
    yr_address_req = models.CharField(max_length=256, verbose_name="Юридический адрес", blank=True, null=True)
    fact_address_req = models.CharField(max_length=256, verbose_name="Фактический адрес", blank=True, null=True)
    phone_req = models.CharField(max_length=256, verbose_name="Телефон (реквизиты)", blank=True, null=True)
    email_req = models.CharField(max_length=256, verbose_name="Электронная почта (реквизиты)", blank=True, null=True)
    okved_req = models.CharField(max_length=100, verbose_name="ОКВЭД", blank=True, null=True)
    okpo_req = models.CharField(max_length=100, verbose_name="ОКПО", blank=True, null=True)
    okato_req = models.CharField(max_length=100, verbose_name="ОКАТО", blank=True, null=True)
    okfs_req = models.CharField(max_length=100, verbose_name="ОКФС", blank=True, null=True)
    okopf_req = models.CharField(max_length=100, verbose_name="ОКОПФ", blank=True, null=True)
    bank_req = models.CharField(max_length=256, verbose_name="Банк", blank=True, null=True)
    bik_req = models.CharField(max_length=100, verbose_name="БИК", blank=True, null=True)
    chet_req = models.CharField(max_length=100, verbose_name="Расчетный счет", blank=True, null=True)
    korr_chet_req = models.CharField(max_length=100, verbose_name="Коректирующий счет", blank=True, null=True)
    nalog_req = models.CharField(max_length=256, verbose_name="Постановка в налоговый учет", blank=True, null=True)
    reg_req = models.CharField(max_length=256, verbose_name="Госрегистрация", blank=True, null=True)
    ogrn_req = models.CharField(max_length=100, verbose_name="ОГРН", blank=True, null=True)
    oktmo_req = models.CharField(max_length=100, verbose_name="ОКТМО", blank=True, null=True)
    director_req = models.CharField(max_length=100, verbose_name="Директор (на основании устава)", blank=True, null=True)

    image = models.ImageField(upload_to='uploads/images', verbose_name="Картинка", blank=True, null=True, editable=False)
    is_main = models.BooleanField(verbose_name="Отображается без поддомена (по умолчанию)", blank=True)
    is_base = models.BooleanField(verbose_name="Популярные города", blank=True,  default=False)
    isHidden = models.BooleanField(verbose_name="Скрыть", blank=True, default=False)
    geo = models.TextField(verbose_name="Код карты", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["order_number", "name"]
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы (Города)"


    def get_subdomain_name(self):
        if self.subdomain_name == '/':
            return ''
        return self.subdomain_name
