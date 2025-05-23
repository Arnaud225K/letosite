# Generated by Django 5.1.5 on 2025-05-14 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0046_alter_product_additional_details_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='additional_details',
            field=models.TextField(blank=True, help_text='Текстовый блок для дополнительной информации.', null=True, verbose_name='Дополнительно (детали)'),
        ),
        migrations.AlterField(
            model_name='product',
            name='country_of_origin',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Страна производства'),
        ),
        migrations.AlterField(
            model_name='product',
            name='delivery_terms_override',
            field=models.TextField(blank=True, help_text='Если отличаются от общих условий.', null=True, verbose_name='Условия доставки (специфичные для товара)'),
        ),
        migrations.AlterField(
            model_name='product',
            name='downloadable_materials_info',
            field=models.TextField(blank=True, null=True, verbose_name='Скачиваемые материалы'),
        ),
        migrations.AlterField(
            model_name='product',
            name='form_of_release',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Форма выпуска'),
        ),
        migrations.AlterField(
            model_name='product',
            name='manufacturer_override',
            field=models.CharField(blank=True, help_text="Используйте, если 'Производитель' из фида неточен", max_length=255, null=True, verbose_name='Производитель (если отличается от Vendor)'),
        ),
        migrations.AlterField(
            model_name='product',
            name='warranty_info',
            field=models.TextField(blank=True, null=True, verbose_name='Гарантия'),
        ),
    ]
