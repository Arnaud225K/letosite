# Generated by Django 5.1.5 on 2025-04-27 04:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0002_alter_searchchange_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='searchchange',
            options={'verbose_name_plural': 'Таб. синонимов (замен)'},
        ),
        migrations.AlterModelOptions(
            name='searchremove',
            options={'verbose_name_plural': 'Таб. исключений'},
        ),
    ]
