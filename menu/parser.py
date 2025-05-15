import logging
import urllib3
import xmltodict
from django.contrib import admin
from django.db.models import Q
from django.utils.text import slugify
from unidecode import unidecode
from .models import FeedLink, MenuCatalog, Product, TypeMenu

import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from urllib.parse import urlparse
import os
from django.conf import settings
import uuid
from django.utils import timezone
from django.db import transaction, IntegrityError
from decimal import Decimal, InvalidOperation

# logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ID_UNCATEGORIZED_CATEGORY = '2'
UNCATEGORIZED_CATEGORY_ID = getattr(settings, 'UNCATEGORIZED_CATEGORY_ID', '2')

# Clé du paramètre contenant le SKU (à adapter si différent dans certains flux)
SKU_PARAM_NAME = getattr(settings, 'FEED_SKU_PARAM_NAME', 'sku')


def download_and_save_image(image_url, product_identifier=""):
    """
    Télécharge et sauvegarde une image, retourne le chemin relatif.
    Vérifie si le fichier existe déjà physiquement.
    """
    if not image_url or not isinstance(image_url, str):
        return None
    log_prefix = f"[Product SKU {product_identifier}]" if product_identifier else "[Image]"
    try:
        # Extraction et nettoyage filename
        path = urlparse(image_url).path
        filename_orig = os.path.basename(path)
        if not filename_orig or '.' not in filename_orig:
            logger.warning(f"{log_prefix} Invalid filename or missing ext for URL: {image_url}")
            return None

        name, ext = os.path.splitext(filename_orig)
        cleaned_name = slugify(unidecode(name)) or f"image-{uuid.uuid4().hex[:8]}"
        max_len = 150 # Limite la longueur pour éviter problèmes système de fichiers
        cleaned_name = cleaned_name[:max_len]
        filename = f"{cleaned_name}{ext.lower()}"

        # Chemin relatif dans MEDIA_ROOT/uploads/import_images/
        file_path_rel = os.path.join('uploads/import_images/', filename)

        # Vérifie l'existence physique
        if default_storage.exists(file_path_rel):
            logger.debug(f"{log_prefix} Image already exists: {file_path_rel}")
            return file_path_rel

        # Télécharge seulement si nécessaire
        logger.info(f"{log_prefix} Downloading image from {image_url} to {file_path_rel}")
        response = requests.get(image_url, stream=True, timeout=30)
        response.raise_for_status()

        # Sauvegarde via Django Storage (gère les conflits de noms si nécessaire)
        saved_path = default_storage.save(file_path_rel, ContentFile(response.content))
        logger.info(f"{log_prefix} Image saved as: {saved_path}")
        return saved_path # Retourne le chemin réel (peut différer si conflit de nom)

    except requests.exceptions.Timeout:
        logger.error(f"{log_prefix} Timeout downloading image: {image_url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"{log_prefix} Error downloading image {image_url}: {e}")
        return None
    except Exception as e:
        logger.exception(f"{log_prefix} Unexpected error saving image {image_url}: {e}")
        return None

def fetch_yml_data(feed_url):
    """Récupère les données YML/XML, gère ETag. Retourne bytes ou None."""
    feed_link_obj = None
    try:
        feed_link_obj = FeedLink.objects.get(feedlink=feed_url)
    except FeedLink.DoesNotExist:
        logger.error(f"FeedLink not configured for URL: {feed_url}")
        return None
    except Exception as e_get:
        logger.error(f"Error fetching FeedLink object for {feed_url}: {e_get}")
        return None

    headers = {}
    if feed_link_obj.etag:
        headers['If-None-Match'] = feed_link_obj.etag.strip('"')

    logger.info(f"[{feed_url}] Fetching data... Sending headers: {headers}")

    try:
        # Utiliser requests qui est généralement plus simple que urllib3 pour ce cas
        response = requests.get(feed_url, headers=headers, timeout=60, stream=True)
        logger.info(f"[{feed_url}] Received status code: {response.status_code}")

        if response.status_code == 304:
            logger.info(f"[{feed_url}] Feed not modified (304). ETag: {feed_link_obj.etag}")
            feed_link_obj.updated_at = timezone.now() # Marque la vérification
            feed_link_obj.save(update_fields=['updated_at'])
            return None

        response.raise_for_status() # Lève une exception pour les autres erreurs >= 400

        # Statut 200 OK
        new_etag = response.headers.get('ETag')
        if new_etag:
            feed_link_obj.etag = new_etag.strip('"')
        else:
            logger.warning(f"[{feed_url}] No ETag received in response headers.")

        feed_link_obj.updated_at = timezone.now()
        feed_link_obj.save(update_fields=['etag', 'updated_at'])
        logger.info(f"[{feed_url}] New data received. New ETag saved: {feed_link_obj.etag}")
        return response.content # Retourne les bytes

    except requests.exceptions.Timeout:
        logger.error(f"[{feed_url}] Request timed out.")
        return None
    except requests.exceptions.RequestException as e_req:
        logger.error(f"[{feed_url}] HTTP Request failed: {e_req}")
        if feed_link_obj: # Met à jour même si erreur fetch
            feed_link_obj.updated_at = timezone.now()
            feed_link_obj.save(update_fields=['updated_at'])
        return None
    except Exception as e_gen:
        logger.exception(f"[{feed_url}] Unexpected error during fetch: {e_gen}")
        return None


def generate_unique_slug(instance, field_to_slugify='title'):
    """Génère un slug unique pour une instance de modèle."""
    if instance is None:
        raise ValueError("Instance cannot be None")

    # Utilise le slug existant si déjà défini
    if instance.slug:
        return instance.slug

    # Prend la valeur du champ spécifié (par défaut 'title')
    text_to_slugify = getattr(instance, field_to_slugify, None)
    if not text_to_slugify:
        # Fallback si le champ source est vide
        slug_base = slugify(f"{instance._meta.model_name}-{instance.pk or uuid.uuid4().hex[:8]}")
    else:
        slug_base = slugify(unidecode(text_to_slugify))
        if not slug_base: # Si le titre ne contient que des caractères non valides
            slug_base = instance._meta.model_name # Fallback au nom du modèle

    # Assure l'unicité
    Klass = instance.__class__
    slug = slug_base
    counter = 1
    # Boucle tant qu'un objet avec ce slug existe DÉJÀ (exclut l'instance actuelle si elle a un pk)
    queryset = Klass.objects.filter(slug=slug)
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    while queryset.exists():
        slug = f"{slug_base}-{counter}"
        queryset = Klass.objects.filter(slug=slug)
        if instance.pk:
            queryset = queryset.exclude(pk=instance.pk)
        counter += 1
        if counter > 100: # Sécurité pour éviter boucle infinie
            logger.error(f"Could not generate unique slug for base '{slug_base}' after 100 attempts.")
            # Retourne un slug potentiellement non unique mais évite boucle infinie
            return f"{slug_base}-{uuid.uuid4().hex[:6]}"
    return slug


def parse_data(data=None, yml_feed_url=None):
    """
    Parse les données YML (ou XML parsable par xmltodict), identifie les produits par SKU,
    met à jour ou crée les produits. Ne traite que les fichiers YML implicitement via xmltodict.
    Retourne True si au moins une offre valide a été traitée, False sinon.
    """
    if data is None:
        logger.warning("parse_data called without data.")
        return False

    feed_id_for_log = yml_feed_url or 'provided_data'
    logger.info(f"[{feed_id_for_log}] Starting parsing process...")

    processed_offer_count = 0
    created_count = 0
    updated_count = 0
    skipped_count = 0
    offers = []

    try:
        # --- Parsing XML/YML ---
        if isinstance(data, bytes): data = data.decode('utf-8')
        if isinstance(data, str): parsed_data = xmltodict.parse(data)
        else: logger.error("Unexpected data type for parsing."); return False

        shop = parsed_data.get('yml_catalog', {}).get('shop', {})
        if not shop: logger.error("Missing 'yml_catalog' or 'shop' root."); return False
        offers_data = shop.get('offers')
        if not offers_data: logger.warning("No 'offers' section found."); return False
        offers = offers_data.get('offer', [])
        if isinstance(offers, dict): offers = [offers]

    except Exception as e_parse:
        logger.exception(f"Error parsing XML/YML structure: {e_parse}")
        return False

    if not offers:
        logger.info("Offer list is empty after parsing.")
        return False

    # --- Récupération Catégorie Non Classé ---
    try:
        uncategorized_category = MenuCatalog.objects.get(id=UNCATEGORIZED_CATEGORY_ID)
    except MenuCatalog.DoesNotExist:
        logger.error(f"CRITICAL: Uncategorized category ID {UNCATEGORIZED_CATEGORY_ID} not found! Cannot proceed.")
        return False

    # --- Traitement des Offres ---
    for offer_dict in offers:
        if not isinstance(offer_dict, dict):
            logger.warning(f"Skipping invalid offer data (not a dict): {type(offer_dict)}")
            skipped_count += 1
            continue

        offer_id_volatile = offer_dict.get('@id', 'N/A')
        offer_name = offer_dict.get('name', '').strip() or f"Unnamed {offer_id_volatile}"

        try:
            # --- 1. Extraction SKU ---
            stable_sku = None
            params_list = offer_dict.get('param', [])
            if isinstance(params_list, dict): params_list = [params_list]
            for param in params_list:
                if isinstance(param, dict) and param.get('@name') == SKU_PARAM_NAME:
                    stable_sku = param.get('#text', '').strip()
                    if stable_sku: break

            if not stable_sku:
                logger.warning(f"[{feed_id_for_log}] Skipping offer (Feed ID: {offer_id_volatile}) - MISSING SKU. Title: {offer_name}")
                skipped_count += 1
                continue

            # --- 2. Préparation Données Formatées ---
            def convert_bool(val_str): return isinstance(val_str, str) and val_str.lower() == 'true'

            # Extraction images (prend la première comme principale si liste)
            pictures = offer_dict.get('picture', [])
            main_image_url = None
            additional_image_urls = []
            if isinstance(pictures, str): main_image_url = pictures
            elif isinstance(pictures, list) and pictures:
                main_image_url = pictures[0]
                additional_image_urls = pictures[1:]

            # Conversion prix
            price = Decimal('0')
            price_str = offer_dict.get('price', '0')
            try: price = Decimal(price_str) if price_str else Decimal('0')
            except InvalidOperation: logger.warning(f"[{feed_id_for_log}] Invalid price for SKU {stable_sku}: '{price_str}'. Using 0.")

            formatted_data = {
                'sku': stable_sku,
                'product_feed_id': offer_id_volatile,
                'title': offer_name,
                'available': convert_bool(offer_dict.get('@available', 'false')),
                'price': price,
                # 'description': offer_dict.get('description', ''),
                'model': offer_dict.get('model', ''),
                'vendor': offer_dict.get('vendor', ''),
                'currencyId': offer_dict.get('currencyId', ''),
                'store': convert_bool(offer_dict.get('store', 'false')),
                'delivery': convert_bool(offer_dict.get('delivery', 'false')),
                'pickup': convert_bool(offer_dict.get('pickup', 'false')),
                'params': {p.get('@name'): p.get('#text', '') for p in params_list if isinstance(p, dict) and p.get('@name')},
                'image_url': main_image_url,
                'additional_image_urls': additional_image_urls,
            }

            # --- 3. Recherche, Mise à Jour ou Création ---
            product_obj = None
            data_changed_in_db = False

            try:
                product_obj = Product.objects.get(sku=stable_sku)
                created = False
                logger.debug(f"[{feed_id_for_log}] Found existing product for SKU {stable_sku}")

                # Compare and update fields
                fields_to_update = []
                for field_name, new_value in formatted_data.items():
                    # Exclure les champs non-modèle ou gérés séparément
                    if field_name in ['sku', 'image_url', 'additional_image_urls']: continue

                    current_value = getattr(product_obj, field_name, None)
                    # Gérer la comparaison pour JSONField (peut être complexe)
                    if isinstance(new_value, dict) or isinstance(current_value, dict):
                        if current_value != new_value: # Comparaison simple de dict
                            setattr(product_obj, field_name, new_value)
                            fields_to_update.append(field_name)
                    elif current_value != new_value:
                        setattr(product_obj, field_name, new_value)
                        fields_to_update.append(field_name)

                # Traitement Images (télécharge si nécessaire)
                new_main_image_path = download_and_save_image(formatted_data['image_url'], stable_sku)
                if str(product_obj.image or '') != str(new_main_image_path or ''):
                    product_obj.image = new_main_image_path
                    fields_to_update.append('image')

                new_additional_paths = [p for img_url in formatted_data['additional_image_urls'] if (p := download_and_save_image(img_url, stable_sku))]
                if product_obj.additional_images != new_additional_paths: # Compare listes
                    product_obj.additional_images = new_additional_paths
                    fields_to_update.append('additional_images')

                # Sauvegarde seulement si des changements ont été détectés
                if fields_to_update:
                    logger.info(f"[{feed_id_for_log}] Updating product SKU {stable_sku} (Fields: {', '.join(fields_to_update)})")
                    # La méthode save() gère availability_changed_at
                    product_obj.save(update_fields=fields_to_update + ['updated_at']) # Sauvegarde seulement les champs modifiés + updated_at
                    updated_count += 1
                else:
                    logger.debug(f"[{feed_id_for_log}] Product SKU {stable_sku} found, no data changes detected.")

            except Product.DoesNotExist:
                # --- CRÉATION ---
                created = True
                logger.info(f"[{feed_id_for_log}] Creating new product for SKU: {stable_sku}")

                image_path = download_and_save_image(formatted_data['image_url'], stable_sku)
                additional_image_paths = [p for img_url in formatted_data['additional_image_urls'] if (p := download_and_save_image(img_url, stable_sku))]

                # Crée l'objet sans le sauvegarder tout de suite pour générer le slug
                product_obj = Product(
                    sku=stable_sku,
                    product_feed_id=formatted_data['product_feed_id'],
                    title=formatted_data['title'],
                    catalog=uncategorized_category,
                    image=image_path,
                    additional_images=additional_image_paths,
                    price=formatted_data['price'],
                    # available=formatted_data['available'],
                    description=formatted_data['description'],
                    model=formatted_data['model'],
                    vendor=formatted_data['vendor'],
                    currencyId=formatted_data['currencyId'],
                    store=formatted_data['store'],
                    delivery=formatted_data['delivery'],
                    pickup=formatted_data['pickup'],
                    params=formatted_data['params'],
                    # Ne pas définir le slug ici
                )
                # Génère le slug basé sur le titre de l'objet non sauvegardé
                product_obj.slug = generate_unique_slug(product_obj)
                # Sauvegarde la première fois
                product_obj.save() # Déclenche la logique save() et availability_changed_at
                created_count += 1

            processed_offer_count += 1

        except IntegrityError as e_int:
            logger.error(f"[{feed_id_for_log}] IntegrityError processing SKU {stable_sku} (FeedID {offer_id_volatile}). Duplicate SKU? Error: {e_int}", exc_info=True)
            skipped_count += 1
        except ValueError as e_val:
            logger.error(f"[{feed_id_for_log}] ValueError processing SKU {stable_sku} (FeedID {offer_id_volatile}). Check data types. Error: {e_val}", exc_info=True)
            skipped_count += 1
        except Exception as e_offer:
            logger.exception(f"[{feed_id_for_log}] Error processing SKU {stable_sku} (FeedID {offer_id_volatile}): {e_offer}")
            skipped_count += 1

    # --- Fin de la Boucle ---
    logger.info(f"[{feed_id_for_log}] Parsing finished. Offers processed: {processed_offer_count}, Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count}.")

    # Retourne True si on a tenté de traiter au moins une offre
    return processed_offer_count > 0 or skipped_count > 0