# Generated by Django 5.1.5 on 2025-03-29 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0024_alter_product_is_hit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='is_hit',
            field=models.BooleanField(db_index=True, default=False, help_text='Показать на главной для хиты', verbose_name='Xит'),
        ),
    ]
