from django.db import models
from django_ckeditor_5.fields import CKEditor5Field



class Uslugi(models.Model):
    order_number = models.PositiveIntegerField("Порядок", default=0, help_text="Порядок отображения")
    name = models.CharField(max_length=255, verbose_name="Название")
    image = models.ImageField(max_length=724, upload_to='uploads/import_images/', null=True, blank=True, verbose_name="Картинка (лучше в .webp)")
    description = models.CharField(max_length=512, verbose_name="Краткое описание")
    text = CKEditor5Field(config_name='extends', verbose_name=" Описание (полный)", blank=True, null=True)
    is_hidden = models.BooleanField(verbose_name="Скрыть", blank=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')


    def __str__(self):
        return self.name

    class Meta:
        ordering = ["order_number"]
        verbose_name = "Услуг"
        verbose_name_plural = "Услуги"

        indexes = [
            # Index pour le filtre is_hidden=False
            models.Index(fields=['is_hidden'], name='idx_uslugi_is_hidden'),
            # Index pour le tri par order_number
            models.Index(fields=['order_number'], name='idx_uslugi_order_number'),
            # Index composite si vous filtrez SOUVENT sur is_hidden ET triez par order_number
            models.Index(fields=['is_hidden', 'order_number'], name='idx_uslugi_hidden_order'),
        ]


