# Generated by Django 5.1.5 on 2025-03-31 09:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_settings', '0002_alter_sociallink_options_sociallink_icon_svg_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='projectsettings',
            options={'ordering': ['id'], 'verbose_name': 'Настройка проекта', 'verbose_name_plural': 'Настройки проекта'},
        ),
    ]
