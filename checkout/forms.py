from django import forms
from django.conf import settings 
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re 
import os 
from .models import Order, Zakaz 

# Taille max en octets (exemple: 5MB)
MAX_UPLOAD_SIZE_BYTES =  5 * 1024 * 1024
# Types MIME autorisés
ALLOWED_CONTENT_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/jpeg',
    'image/png',
    'image/webp',
    'image/gif',
]
# Extensions
ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.webp', '.gif']
# -------------------------------------------------------------------------

class OrderCreateForm(forms.ModelForm):
    name = forms.CharField(
        label="Ф.И.О", max_length=100, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Введите ваше Ф.И.О.'})
    )
    email = forms.EmailField(
        label="Email", required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'example@mail.com'})
    )
    phone = forms.CharField(
        label="Телефон", max_length=20, required=True,
        widget=forms.TextInput(attrs={'placeholder': '+7 (___) ___-__-__', 'type': 'tel'})
    )
    address = forms.CharField(
        label="Адрес доставки", max_length=255, required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Город, улица, дом, квартира...', 'rows': 3})
    )
    payment_method = forms.ChoiceField(
        label="Способ оплаты", choices=Order.PAYMENT_METHOD_CHOICES, required=True,
        widget=forms.RadioSelect,
        initial=Order.PAYMENT_GET_OFFER
    )
    type_client = forms.ChoiceField(
        label="Тип клиента", choices=Order.CLIENT_TYPE_CHOICES, required=True,
        widget=forms.RadioSelect,
        initial=Order.TYPE_INDIVIDUAL
    )
    file = forms.FileField(
        label="Прикрепить файл (реквизиты)", required=False,
        help_text="Макс. размер: {} МБ.".format(
            int(MAX_UPLOAD_SIZE_BYTES / (1024*1024)),
        )
    )
    agreement = forms.BooleanField(
        required=True,
        error_messages={'required': 'Вы должны согласиться на обработку персональных данных.'},
        widget=forms.HiddenInput(attrs={'value':'true'})
    )

    class Meta:
        model = Order
        fields = ['name', 'email', 'phone', 'address', 'type_client', 'payment_method', 'file']

    def clean_phone(self):
        """Valide et nettoie le numéro de téléphone."""
        phone_number = self.cleaned_data.get('phone')
        if not phone_number:
            return phone_number

        #  Removes everything except numbers
        cleaned_phone = re.sub(r'\D', '', phone_number)

        # Get 8 initial
        if cleaned_phone.startswith('8') and len(cleaned_phone) == 11:
            cleaned_phone = '7' + cleaned_phone[1:]

        #  Regex Validation (11 number begin with 7)
        russian_phone_regex = r'^7\d{10}$'
        if not re.match(russian_phone_regex, cleaned_phone):
            raise forms.ValidationError(
                _("Пожалуйста, введите действительный российский номер телефона (напр., +7 9XX XXX-XX-XX)."),
                code='invalid_phone_format'
            )
        
        return phone_number

    # --- File ---
    def clean_file(self):
        """Valide la taille et le type du fichier uploadé."""
        file = self.cleaned_data.get('file')
        if file:
            if file.size > MAX_UPLOAD_SIZE_BYTES:
                raise forms.ValidationError(
                    _("Файл «%(filename)s» слишком большой. Максимальный размер: %(max_size)s МБ."),
                    params={'filename': file.name, 'max_size': int(MAX_UPLOAD_SIZE_BYTES / (1024*1024))},
                    code='file_too_large'
                )

            if file.content_type not in ALLOWED_CONTENT_TYPES:
                raise forms.ValidationError(
                    _("Недопустимый тип файла «%(filename)s» (%(type)s)."),
                    params={'filename': file.name, 'type': file.content_type},
                    code='invalid_file_type'
                )

            ext = os.path.splitext(file.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise forms.ValidationError(
                    _("Недопустимое расширение файла «%(filename)s». Разрешены: %(exts)s"),
                    params={'filename': file.name, 'exts': ', '.join(ALLOWED_EXTENSIONS)},
                    code='invalid_file_extension'
                )

        return file

    def clean(self):
        """Validation globale après le nettoyage de chaque champ."""
        cleaned_data = super().clean()
        type_client = cleaned_data.get("type_client")
        file = cleaned_data.get("file")

        if type_client == Order.TYPE_LEGAL_ENTITY and not file:
            if 'file' not in self.errors:
                self.add_error('file', 'Для юридических лиц необходимо прикрепить файл реквизитов.')

        return cleaned_data
    


class ZakazForm(forms.ModelForm):
    # Les champs requis correspondent à ceux du formulaire HTML
    name = forms.CharField(label="Ф.И.О", max_length=50, required=False)
    email = forms.EmailField(label="E-mail", max_length=50, required=True)
    phone = forms.CharField(label="Телефон", max_length=20, required=True)
    comment = forms.CharField(label="Комментарий", required=False, widget=forms.HiddenInput()) # Champ caché pour commentaire
    type = forms.CharField(label="Тип", max_length=128, required=False, widget=forms.HiddenInput()) # Nom différent pour éviter conflit avec 'type' python

    # Honeypot
    form_input = forms.CharField(required=False, widget=forms.HiddenInput())

    # Accord (Pas un champ modèle, validé séparément ou dans clean())
    agreement = forms.BooleanField(required=False, error_messages={'required': 'Необходимо согласие.'})


    class Meta:
        model = Zakaz
        fields = ['name', 'email', 'phone', 'text']
        # Exclut: date, ip_address, last_updated, type_order, email_to (gérés par la vue)

    def clean_phone(self):
        phone_number = self.cleaned_data.get('phone')
        if phone_number:
            cleaned_phone = re.sub(r'\D', '', phone_number)
            if cleaned_phone.startswith('8'): cleaned_phone = '7' + cleaned_phone[1:]
            russian_phone_regex = r'^7\d{10}$'
            if not re.match(russian_phone_regex, cleaned_phone):
                raise forms.ValidationError("Неверный формат номера телефона.")
            return phone_number
        return phone_number

    def clean_form_input(self):
        """Vérifie le champ Honeypot."""
        honeypot = self.cleaned_data.get('form_input')
        if honeypot:
            raise forms.ValidationError("Обнаружена подозрительная активность.", code='honeypot') 
        return honeypot

    def clean(self):
        cleaned_data = super().clean()
        # Ajoutez ici la validation reCAPTCHA si vous l'utilisez
        # token = cleaned_data.get('token')
        # if not validate_recaptcha(token): # Votre fonction de validation
        #     raise forms.ValidationError("Ошибка проверки reCAPTCHA.", code='recaptcha_failed')
        return cleaned_data