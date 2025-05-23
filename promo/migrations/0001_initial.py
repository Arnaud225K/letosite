# Generated by Django 5.1.5 on 2025-05-14 06:39

import promo.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Promo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.PositiveIntegerField(default=0, verbose_name='Порядок отображения')),
                ('name', models.CharField(max_length=512, unique=True, verbose_name='Название')),
                ('slug', models.SlugField(blank=True, max_length=512, null=True, unique=True, verbose_name='Название латинское')),
                ('description', models.TextField(blank=True, help_text='Краткое описание акции', null=True, verbose_name='Описание')),
                ('text', models.TextField(blank=True, help_text='Описание', null=True, verbose_name='Текст')),
                ('image', models.ImageField(blank=True, help_text='Максимум 2MB', null=True, upload_to='uploads/images', validators=[promo.models.validate_image_size], verbose_name='Картинка основная')),
                ('image_2', models.ImageField(blank=True, help_text='Максимум 2MB', null=True, upload_to='uploads/images', validators=[promo.models.validate_image_size], verbose_name='Вторая картинка')),
                ('is_show_main', models.BooleanField(default=False, help_text='Отображать на главной странице', verbose_name='Показывать на главной')),
                ('is_hidden', models.BooleanField(default=False, help_text='Скрыть акцию с публичных страниц', verbose_name='Скрыть')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
            ],
            options={
                'verbose_name': 'Акция',
                'verbose_name_plural': 'Акции',
                'ordering': ['order_number', '-created_at'],
                'indexes': [models.Index(fields=['is_show_main', 'is_hidden'], name='promo_promo_is_show_e9956d_idx')],
            },
        ),
    ]
