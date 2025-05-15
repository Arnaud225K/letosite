import os
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save

def validate_image_size(image):
    # Validation de la taille de l'image (max 2MB)
    if image.size > 2 * 1024 * 1024:
        raise ValidationError("Размер изображения не должен превышать 2MB!")

class Promo(models.Model):
    order_number = models.PositiveIntegerField(verbose_name="Порядок отображения",default=0)
    name = models.CharField(max_length=255, verbose_name="Название", unique=True)
    slug = models.SlugField(max_length=255, verbose_name="Название латинское", unique=True, blank=True, null=True)
    description = models.TextField(verbose_name="Описание", blank=True, null=True, help_text="Краткое описание акции")
    text = models.TextField(verbose_name="Текст", blank=True, null=True, help_text="Описание")
    image = models.ImageField(upload_to='uploads/images', verbose_name="Картинка основная", blank=True, null=True, validators=[validate_image_size], help_text="Максимум 2MB")
    image_2 = models.ImageField(upload_to='uploads/images', verbose_name="Вторая картинка", blank=True, null=True, validators=[validate_image_size], help_text="Максимум 2MB")
    is_show_main = models.BooleanField( verbose_name="Показывать на главной", default=False, help_text="Отображать на главной странице")
    is_hidden = models.BooleanField( verbose_name="Скрыть", default=False, help_text="Скрыть акцию с публичных страниц")
    created_at = models.DateTimeField( auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField( auto_now=True, verbose_name='Обновлено')

    class Meta:
        ordering = ["order_number", "-created_at"]
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        indexes = [
            models.Index(fields=['is_show_main', 'is_hidden']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('promo', kwargs={'slug': self.slug})

def pre_save_slug(sender, instance, **kwargs):
    if not instance.slug and instance.name:
        instance.slug = slugify(instance.name, allow_unicode=True)

pre_save.connect(pre_save_slug, sender=Promo)
