
import os
from django.core.files.storage import FileSystemStorage
from letosite import settings
from urllib.parse import urljoin
from datetime import datetime

from django.utils.html import format_html
from django.templatetags.static import static

from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, message
from django.conf import settings


import logging

logger = logging.getLogger(__name__)

DEFAULT_ADMIN_ICON_PLACEHOLDER = getattr(settings, 'DEFAULT_ADMIN_IMAGE_PLACEHOLDER', 'img/images/default_image.webp')



class CkeditorCustomStorage(FileSystemStorage):
    """
    Кастомное расположение для медиа файлов редактора
    """
    def get_folder_name(self):
        return datetime.now().strftime('%Y/%m/%d')

    def get_valid_name(self, name):
        return name

    def _save(self, name, content):
        folder_name = self.get_folder_name()
        name = os.path.join(folder_name, self.get_valid_name(name))
        return super()._save(name, content)

    location = os.path.join(settings.MEDIA_ROOT, 'uploads/')
    base_url = urljoin(settings.MEDIA_URL, 'uploads/')



def get_admin_image_thumbnail_html(instance, image_field_name='image', alt_text_base="Изображение", width=50, height=50):
    """
    Génère le HTML pour une miniature d'image pour l'admin Django.
    Gère les images manquantes et les erreurs.

    Args:
        instance: L'instance du modèle (ex: un objet Product ou MenuCatalog).
        image_field_name (str): Le nom de l'attribut ImageField/FileField sur l'instance.
        alt_text_base (str): Texte de base pour l'attribut alt/title.
        width (int): Largeur de la miniature.
        height (int): Hauteur de la miniature.

    Returns:
        str: Une chaîne HTML sûre (via format_html) ou un texte de fallback.
    """
    image_url = None
    alt_text = alt_text_base
    try:
        image_field = getattr(instance, image_field_name, None)
        if image_field and hasattr(image_field, 'url'):
            try:
                image_url = image_field.url
            except ValueError:
                logger.warning(f"Model {instance.__class__.__name__} PK {instance.pk}: File missing for ImageField '{image_field_name}' ({getattr(image_field, 'name', 'N/A')})")
                image_url = None 

        if image_url:
            final_html = format_html(
                '<img src="{}" width="{}" height="{}" alt="{}" style="object-fit:contain; vertical-align: middle; border-radius: 4px;" />',
                image_url, width, height, alt_text,)
        else:
            try:
                placeholder_url = static(DEFAULT_ADMIN_ICON_PLACEHOLDER)
                final_html = format_html(
                    '<img src="{}" width="{}" height="{}" alt="Нет изображения" title="Нет изображения" style="object-fit:contain; vertical-align: middle; filter: grayscale(80%); opacity: 0.7;" />',
                    placeholder_url, width, height
                )
            except Exception as e_static:
                logger.error(f"Could not find default static placeholder image '{DEFAULT_ADMIN_ICON_PLACEHOLDER}': {e_static}")
    except Exception as e_main:
        logger.error(f"Error generating thumbnail for {instance.__class__.__name__} PK {instance.pk}, field '{image_field_name}': {e_main}", exc_info=True)
    return final_html


def send_notification(mail_subject, mail_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(mail_template, context)
    if(isinstance(context['to_email'], str)):
        to_email = []
        to_email.append(context['to_email'])
    else:
        to_email = context['to_email']
    mail = EmailMessage(mail_subject, message, from_email, to=to_email)
    mail.content_subtype = "html"
    mail.send()