from django.db import models
from django.utils.html import format_html
from django.conf import settings 
from django.templatetags.static import static

DEFAULT_ADMIN_ICON_PLACEHOLDER = getattr(settings, 'DEFAULT_ADMIN_IMAGE_PLACEHOLDER', 'img/images/default_image.webp')

class ProjectSettings(models.Model):
	name = models.CharField(max_length=256, verbose_name="Название компании")
	site_name = models.CharField(max_length=256, verbose_name="Название сайта")
	logo = models.ImageField(upload_to='uploads/images', verbose_name="Логотип", blank=True, null=True)
	title_text_index = models.CharField(max_length=256, verbose_name="Заголовок текста на главной странице", blank=True, null=True)
	
	type_company = models.CharField(max_length=256, verbose_name="Тип компании", blank=True, null=True)
	count_staff = models.CharField(max_length=256, verbose_name="Количество сотрудников", blank=True, null=True)
	start_year = models.CharField(max_length=50, verbose_name="Год основания", blank=True, null=True)
	
	text_head = models.TextField(verbose_name="Блок в head (внизу)", blank=True, null=True)
	text_body = models.TextField(verbose_name="Блок в body (внизу)", blank=True, null=True)
	
	tech_mail_server = models.CharField(max_length=256, verbose_name="Почтовый сервер (для отправки сообщений)")
	tech_email = models.CharField(max_length=256, verbose_name="Почта для отправки сообщений")
	tech_email_pass = models.CharField(max_length=256, verbose_name="Пароль почты для отправки сообщений")
	
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ["id"]
		verbose_name = "Настройка проекта"
		verbose_name_plural = "Настройки проекта"


# class SocialLink(models.Model):
# 	icon_name = models.CharField(max_length=128, verbose_name="Название значка", default="")
# 	name = models.CharField(max_length=1024, verbose_name="Ссылка")
# 	is_hidden = models.BooleanField(verbose_name="Скрыть", blank=True, default=False)
# 	project_settings = models.ForeignKey(ProjectSettings, on_delete=models.CASCADE)

class SocialLink(models.Model):
    order_number = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Порядок")
    icon_name = models.CharField(max_length=128, verbose_name="Название значка (для справки)", default="", blank=True)
    name = models.CharField(max_length=724, verbose_name="URL ссылки")
    # icon_svg = models.TextField(verbose_name="Код SVG иконки", blank=True, null=True, help_text="Вставьте полный код SVG сюда")
    icon_image = models.ImageField(upload_to="uploads/images", verbose_name="Картинка", blank=True, null=True)
    is_hidden = models.BooleanField(verbose_name="Скрыть", blank=True, default=False)
    project_settings = models.ForeignKey(ProjectSettings, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def display_svg_icon(self):
            """Affiche une miniature de l'image uploadée ou un placeholder."""
            image_url = None
            alt_text = "Иконка"
            if self.icon_image and hasattr(self.icon_image, 'url'):
                try:
                    image_url = self.icon_image.url
                    alt_text = f"Иконка для {self.name or self.icon_name or 'ссылки'}"
                except ValueError:
                    image_url = None

            if image_url:
                return format_html(
                    '<img src="{}" width="30" height="30" alt="{}" title="{}" style="object-fit:contain; border-radius: 4px; vertical-align: middle;" />', image_url, alt_text, alt_text)
            else:
                try:
                    placeholder_url = static(DEFAULT_ADMIN_ICON_PLACEHOLDER)
                    return format_html(
                        '<img src="{}" width="30" height="30" alt="Нет изображения" title="Нет изображения" style="object-fit:contain; border-radius: 4px; vertical-align: middle; filter: grayscale(80%); opacity: 0.7;" />', placeholder_url)
                except Exception:
                    return "Нет изображения"
    display_svg_icon.short_description = 'Картинка'


    class Meta:
        ordering = ['order_number', 'name']
        verbose_name = "Социальная ссылка"
        verbose_name_plural = "Социальные ссылки"