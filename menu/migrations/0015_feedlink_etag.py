# Generated by Django 5.1.5 on 2025-02-07 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0014_alter_menucatalog_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedlink',
            name='etag',
            field=models.CharField(blank=True, max_length=724, null=True),
        ),
    ]
