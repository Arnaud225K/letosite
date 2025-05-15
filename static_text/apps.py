from django.apps import AppConfig


class StaticTextConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'static_text'
    verbose_name = 'Статические тексты'
