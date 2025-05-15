from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView, View
from .models import MenuCatalog, Product, TypeMenu, FilterCategory, FilterValue
from promo.models import Promo
from uslugi.models import Uslugi
from filials.views import get_current_filial
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.http import HttpResponseNotFound, HttpResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, Page
from django.http import HttpResponse, JsonResponse, Http404
from django.urls import reverse
import logging
from django.utils.text import slugify
from django.db.models.functions import Concat
from django.db.models import Q, Case, When, IntegerField, Value, Count, Prefetch
import random
from django.conf import settings
from collections import defaultdict
import urllib.parse
from django.template.loader import render_to_string
from unidecode import unidecode 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


SIZE_SALE_INDEX = 20
PRODUCTS_PER_PAGE = 12
SIZE_OFFERS_INDEX = 4
MAX_ITEM = 20

UNCATEGORIZED_CATEGORY_ID = getattr(settings, 'UNCATEGORIZED_CATEGORY_ID', '2')
VALID_SIMILAR_TYPE_IDS = getattr(settings, 'VALID_SIMILAR_CATEGORY_TYPE_IDS', ['6', '7', '8'])
CATALOG_ROOT_SLUG = 'catalog'
PRIMARY_MENU_TYPES = ['6', '7', '8']

################################
####### SORT PRODUCT #######
################################
def get_sort_type(sort_type, product_list):
    if sort_type == 'price_asc':
        return "Price Asc", product_list.order_by('price')
    elif sort_type == 'price_desc':
        return "Price Desc", product_list.order_by('-price')
    else:
        return "Default", product_list.order_by('title')

# def get_sort_type_display(sort_type):
#      """Retourne le nom lisible du tri."""
#      sort_options = dict([ ('', 'По умолчанию'), ('price_asc', 'По возрастанию цены'), ('price_desc', 'По убыванию цены')])
#      return sort_options.get(sort_type, 'По умолчанию')
################################
####### SIMIALR CATEGORY #######
################################
def get_similar_categories_optimized(current_category, min_results=6, fallback_to_parent=True):
    """
    Récupère une liste de MenuCatalog similaires (CLASSIFIÉS et du bon TYPE)
    à une catégorie donnée, de manière optimisée.

    Stratégie :
    1. Vérifie l'input.
    2. Définit les filtres.
    3. Construit dynamiquement les clauses When pour la priorisation.
    4. Exécute UNE requête optimisée avec annotation de priorité.
    5. Mélange et limite en Python.
    """
    # --- Validation Input ---
    if not isinstance(current_category, MenuCatalog):
        logger.error(f"get_similar_categories: Expected MenuCatalog instance, got {type(current_category)}")
        return []
    if not current_category.pk:
        logger.warning("get_similar_categories: current_category has no PK.")
        return []
    if str(current_category.id) == UNCATEGORIZED_CATEGORY_ID:
        logger.debug(f"Category {current_category.pk} is uncategorized. No similar search.")
        return []
    # Optionnel: Vérifier le type de la catégorie actuelle
    # if str(current_category.type_menu_id) not in VALID_SIMILAR_TYPE_IDS:
    #     logger.debug(f"Category {current_category.pk} has invalid type for similarity search.")
    #     return []

    parent = current_category.parent
    grandparent = parent.parent if parent else None

    # --- Construction Filtres de Base ---
    filters = Q(is_hidden=False)                       # Doit être visible
    filters &= ~Q(pk=current_category.pk)              # Ne pas s'inclure soi-même
    filters &= ~Q(id=UNCATEGORIZED_CATEGORY_ID)        # Exclure la catégorie non classée
    filters &= Q(type_menu_id__in=VALID_SIMILAR_TYPE_IDS) # Filtre sur les types valides

    # --- Construction dynamique des clauses When ---
    when_clauses = []
    # Priorité 1: Sœurs (si parent existe)
    if parent:
        when_clauses.append(When(parent=parent, then=Value(1)))
    # Priorité 2: Cousines (si grand-parent existe)
    # Note: parent__parent=grandparent inclut aussi les sœurs, mais elles auront déjà matché Prio 1
    if grandparent:
        # La condition When(parent=parent) précédente aura déjà priorisé les sœurs
        when_clauses.append(When(parent__parent=grandparent, then=Value(2)))
    # Priorité 3: Catégories racine
    when_clauses.append(When(parent=None, then=Value(3)))
    # --------------------------------------------

    # --- Priorisation avec Case/When ---
    priority_expression = Case(
        *when_clauses,         # Dépaquette la liste des clauses When valides
        default=Value(99),     # Priorité très basse pour tout le reste (au cas où)
        output_field=IntegerField()
    )

    # --- Champs à récupérer ---
    fields_to_load = ('pk', 'name', 'slug', 'image', 'parent', 'parent_id', 'order_number', 'type_menu_id') # Inclut parent_id

    # --- Requête Principale ---
    try:
        logger.debug(f"Similar Categories Optimized: Searching around category '{current_category.name}' (ID: {current_category.pk}) for types {VALID_SIMILAR_TYPE_IDS}")

        potential_limit = min_results * 3 # Récupère plus pour le mélange

        # --- Exécution de la requête ---
        potential_similars_qs = MenuCatalog.objects.filter(
            filters
        ).annotate(
            priority=priority_expression
        ).select_related('parent', 'type_menu').only(*fields_to_load).order_by(
            'priority',        # Trie par priorité calculée
            '-order_number',   # Puis par ordre (ajustez si ascendant)
            'name'             # Puis par nom
        )[:potential_limit]

        # --- Conversion en liste d'objets (partiels) ---
        potential_similars_list = list(potential_similars_qs)

        if not potential_similars_list:
            logger.debug("No potential similar categories found matching criteria.")
            return []

        # --- Fallback logique (Optionnel - Moins prioritaire avec Case/When mais peut compléter) ---
        # La priorisation avec Case/When devrait déjà bien classer,
        # rendant le fallback explicite moins nécessaire, mais on peut le garder
        # pour garantir le nombre si les priorités hautes ne suffisent pas.

        current_results_count = len(potential_similars_list)
        ids_already_found = {cat.pk for cat in potential_similars_list} | {current_category.pk}

        # Fallback explicite vers le parent (si nécessaire et non déjà couvert par priorité 2)
        # Note: Théoriquement, priorité 2 devrait déjà trouver les cousines.
        # Cette section de fallback devient redondante si Case/When fonctionne bien.
        # Je la laisse commentée pour référence mais la logique de priorité est meilleure.
        # if fallback_to_parent and current_results_count < min_results and parent and str(parent.id) != UNCATEGORIZED_CATEGORY_ID:
        #     needed = min_results - current_results_count
        #     logger.debug(f"Explicit Fallback: Checking parent {parent.pk}. Need {needed}")
        #     parent_level_qs = MenuCatalog.objects.filter(filters, parent=parent).exclude(pk__in=ids_already_found).only(*fields_to_load).order_by(...)[:needed]
        #     parent_level_results = list(parent_level_qs)
        #     if parent_level_results:
        #         potential_similars_list.extend(parent_level_results)
        #         ids_already_found.update(cat.pk for cat in parent_level_results)

        # Fallback vers Top-Level (si nécessaire et non déjà couvert par priorité 3)
        # if len(potential_similars_list) < min_results:
            # needed = min_results - len(potential_similars_list)
            # logger.debug(f"Explicit Fallback: Checking top-level. Need {needed}")
            # top_level_qs = MenuCatalog.objects.filter(filters, parent=None).exclude(pk__in=ids_already_found).only(*fields_to_load).order_by('?')[:needed]
            # top_level_results = list(top_level_qs)
            # potential_similars_list.extend(top_level_results)

        # --- Mélange et Sélection Finale ---
        logger.debug(f"Total found before shuffle: {len(potential_similars_list)}. Shuffling and taking {min_results}.")
        random.shuffle(potential_similars_list) # Mélange la liste
        return potential_similars_list[:min_results] # Retourne les objets MenuCatalog partiels

    except Exception as e:
        logger.exception(f"Error getting optimized similar categories for {current_category.pk}: {e}")
        return []

def get_similar_products(product, max_results=6, fallback_to_parent=True):
    """
    Récupère une liste de produits similaires (CLASSIFIÉS) à un produit donné,
    en incluant à la fois les produits disponibles et indisponibles.

    Stratégie optimisée :
    1. Exclut la catégorie "Non classé" et le produit actuel.
    2. Cherche dans la catégorie actuelle (dispos et indispos).
    3. Si fallback et pas assez, cherche dans la catégorie parente (si classifiée).
    4. Combine, mélange et limite les résultats.
    """
    if not product or not product.catalog:
        logger.warning(f"get_similar_products: Product {product.pk if product else 'None'} has no catalog.")
        return []

    current_category = product.catalog

    # Ne pas chercher si produit actuel est non classé
    if str(current_category.id) == UNCATEGORIZED_CATEGORY_ID:
        logger.debug(f"get_similar_products: Product {product.pk} is in uncategorized. No similar products.")
        return []

    product_pk_to_exclude = {product.pk}
    similar_products_list = []

    # On filtre seulement sur is_hidden et la catégorie non classée
    common_filters = Q(is_hidden=False)
    common_filters &= ~Q(catalog__id=UNCATEGORIZED_CATEGORY_ID) # Exclut non classé

    # AJOUT de 'available' pour pouvoir l'afficher si besoin dans le template
    fields_to_load = ('pk', 'title', 'slug', 'image', 'price', 'currencyId', 'available', 'catalog__name')

    try:
        # --- 1. Recherche dans la Même Catégorie ---
        logger.debug(f"Similar products: Searching in category '{current_category.name}' (ID: {current_category.pk}) including unavailable.")
        same_category_qs = Product.objects.filter(
            common_filters,
            catalog=current_category
        ).exclude(
            pk=product.pk
        ).only(*fields_to_load).order_by('-is_hit', '-created_at')

        # Prend un peu plus pour le mélange
        limit_same_cat = max_results + 4
        same_category_results = list(same_category_qs[:limit_same_cat])
        similar_products_list.extend(same_category_results)
        logger.debug(f"Found {len(same_category_results)} products in same category (incl. unavailable, excl. uncategorized).")

        found_product_ids = {p.pk for p in similar_products_list} | product_pk_to_exclude

        # --- 2. Fallback vers la Catégorie Parente ---
        remaining_needed = max_results - len(similar_products_list)
        parent_category = current_category.parent

        if fallback_to_parent and remaining_needed > 0 and parent_category:
            if str(parent_category.id) != UNCATEGORIZED_CATEGORY_ID:
                limit_parent = remaining_needed + 4
                logger.debug(f"Checking parent '{parent_category.name}' (ID: {parent_category.pk}). Need {remaining_needed}, fetching up to {limit_parent}.")

                parent_products_qs = Product.objects.filter(
                    common_filters,
                    catalog=parent_category
                ).exclude(
                    pk__in=found_product_ids
                ).only(*fields_to_load).order_by('-is_hit', '-created_at')

                parent_products_list = list(parent_products_qs[:limit_parent])
                logger.debug(f"Found {len(parent_products_list)} products in parent category.")
                similar_products_list.extend(parent_products_list)
            else:
                logger.debug(f"Parent category is uncategorized. Skipping fallback.")

        # --- 3. Mélange et Limitation Finale ---
        if similar_products_list:
            logger.debug(f"Total found before shuffle: {len(similar_products_list)}. Shuffling and taking {max_results}.")
            random.shuffle(similar_products_list)
            return similar_products_list[:max_results]
        else:
            logger.debug("No similar classified products found.")
            return []

    except Exception as e:
        logger.exception(f"Error getting similar products for product {product.pk}: {e}")
        return []

# ----------------------------------------------------

def parse_filters_from_url(filter_path_segment):
    """
    Parse le segment /f/cat1=val1,val2/cat2=val3/ en un dict.
    Exemple: "proizvoditel=aquaviva/tolshina=100,120"
    Retourne: {'proizvoditel': ['aquaviva'], 'tolshina': ['100', '120']}
    """
    active_filters = {}
    if not filter_path_segment:
        return active_filters # Retourne dict vide si pas de segment

    # Enlève le /f/ initial ou final si présent et split par /
    filter_part = filter_path_segment.strip('/')
    if filter_part.startswith('f/'): # Sécurité supplémentaire
        filter_part = filter_part[2:]
    pairs = filter_part.split('/')

    for pair in pairs:
        if '=' in pair:
            # Sépare clé et valeurs
            key, values_str = pair.split('=', 1)
            # Nettoie la clé (slug)
            key = key.strip()
            # Sépare les valeurs multiples par virgule, nettoie les espaces
            values = [urllib.parse.unquote(v.strip()) for v in values_str.split(',') if v.strip()] # Décode les valeurs URL-encodées
            if key and values:
                active_filters[key] = values # Stocke la liste des valeurs pour cette clé
        else:
            logger.warning(f"Could not parse filter pair (missing '='): '{pair}' in segment '{filter_path_segment}'")

    logger.debug(f"Parsed URL filters: {active_filters}")
    return active_filters


# --- Fonctions Utilitaires Locales ---

def parse_filters_from_request(request_get):
    """ Parse les filtres depuis request.GET (ex: ?proizvoditel=aquaviva&tsvet=belyy). """
    active_filters = defaultdict(list)
    for key, value_list in request_get.lists(): # Utilise lists()
        if key not in ['page', 'sort', 'q', 'category_slug']: # Exclut params connus non-filtre
             if value_list:
                 # Clé = slug catégorie filtre, Valeurs = liste slugs valeurs filtre
                 active_filters[key].extend(v for v in value_list if v)
    return dict(active_filters)

# def apply_filters_to_queryset(product_qs, active_filters_dict):
#     """ Applique les filtres M2M au queryset Product. """
#     if not active_filters_dict:
#         return product_qs
#     base_filter = Q()
#     for category_slug, value_slugs in active_filters_dict.items():
#         if value_slugs:
#              base_filter &= Q(filters__category__slug=category_slug, filters__slug__in=value_slugs)
#     # Utilise distinct() pour éviter doublons si produit a plusieurs valeurs cochées OU si plusieurs filtres actifs
#     return product_qs.filter(base_filter).distinct()

def apply_filters_to_queryset(product_qs, active_filters_dict):
    if not active_filters_dict:
        return product_qs
    
    # filtered_qs = product_qs # Ne pas réassigner ici, on filtre directement
    
    # Chaque itération affine le queryset
    for category_slug, value_slugs in active_filters_dict.items():
        if value_slugs:
            logger.debug(f"Applying filter to QS: category='{category_slug}', values IN {value_slugs}")
            # Crée une condition Q pour OR entre les valeurs d'UNE MÊME catégorie de filtre
            q_values_for_category = Q()
            for val_slug in value_slugs:
                q_values_for_category |= Q(filters__slug=val_slug, filters__category__slug=category_slug)
            
            # Filtre le queryset principal avec cette condition OR
            # Si plusieurs catégories de filtres sont actives (cvet ET tolshina),
            # cela va appliquer un AND entre les Q objets des différentes catégories
            # grâce aux appels successifs à .filter()
            product_qs = product_qs.filter(q_values_for_category)

    # Le .distinct() est crucial à la fin pour les relations M2M
    return product_qs.distinct()

def build_filter_url_segment(active_filters):
    """ Construit le segment /f/cat1=val1,val2/cat2=val3/. """
    if not active_filters: return ""
    parts = []
    for key in sorted(active_filters.keys()): # Trie clés
        values = sorted(active_filters[key]) # Trie valeurs
        if values: parts.append(f"{key}={','.join(values)}")
    if not parts: return ""
    return "f/" + "/".join(parts) + "/"
# ----------------------------------------------------

# --- NOUVELLE Fonction Utilitaire (ou à mettre dans la classe View) ---
def get_active_filters_display_string(active_filters_dict, filter_categories_qs=None):
    """
    Construit une chaîne lisible des filtres actifs.
    Exemple: "Производитель: Aquaviva, Цвет: Белый"
    """
    if not active_filters_dict:
        return ""

    parts = []
    # Récupère les noms lisibles des catégories de filtres (optimisation)
    if filter_categories_qs is None:
        # Requête si pas fourni (moins optimal si appelé souvent)
        filter_categories_qs = FilterCategory.objects.filter(slug__in=active_filters_dict.keys(), is_active=True)

    category_names_map = {fc.slug: fc.name for fc in filter_categories_qs}

    # Trie par nom de catégorie de filtre pour un affichage cohérent
    for cat_slug in sorted(active_filters_dict.keys()):
        cat_name = category_names_map.get(cat_slug, cat_slug.replace('_', ' ').capitalize()) # Fallback
        values_slugs = active_filters_dict[cat_slug]

        # Récupère les noms lisibles des valeurs de filtres (optimisation)
        value_names = list(FilterValue.objects.filter(
            category__slug=cat_slug,
            slug__in=values_slugs
        ).values_list('value', flat=True))

        if value_names:
            parts.append(f"{cat_name}: {', '.join(value_names)}")

    return ", ".join(parts)
# ---------------------------------------------------------------

def ajax_get_menu_dropdown_content(request):
    """
    Retourne le fragment HTML pour le menu dropdown.
    Les onglets sont les enfants de "Каталог" du bon type.
    Le contenu des onglets sont les enfants de ces onglets.
    """
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponse("AJAX request required.", status=400)

    logger.debug("AJAX request for menu dropdown content...")
    menu_tabs_items = MenuCatalog.objects.none() # Initialise à vide

    try:
        # 1. Trouver l'élément racine "Каталог"
        try:
            catalog_root = MenuCatalog.objects.get(slug=CATALOG_ROOT_SLUG, parent__isnull=True, is_hidden=False)
            logger.debug(f"Found catalog root: {catalog_root.name}")
        except MenuCatalog.DoesNotExist:
            logger.error(f"CRITICAL: Catalog root item with slug '{CATALOG_ROOT_SLUG}' not found or hidden.")
            # Si la racine "Каталог" est indispensable, on peut s'arrêter ici.
            # Ou, si "Каталог" est juste le lien du header et n'est pas un parent réel en DB pour les items de type 6,7,8:
            # Dans ce dernier cas, on prendrait directement les items de premier niveau des bons types.
            # Pour l'instant, on suppose que "Каталог" EST le parent.
            return HttpResponse("<p>Ошибка: Корневой каталог не найден.</p>", status=500)

        # 2. Récupérer les enfants de "Каталог" pour les onglets (Niveau 1 du dropdown)
        #    Filtrer par type et exclure l'ID si spécifié
        tab_filters = Q(is_hidden=False) & Q(type_menu_id__in=VALID_SIMILAR_TYPE_IDS)
        if UNCATEGORIZED_CATEGORY_ID:
            tab_filters &= ~Q(id=UNCATEGORIZED_CATEGORY_ID)

        menu_tabs_items = catalog_root.menucatalog_set.filter(tab_filters).order_by(
            'order_number', 'name'
        ).prefetch_related(
            # Précharger les enfants (Niveau 2 du dropdown) de chaque item d'onglet
            Prefetch(
                'menucatalog_set',
                queryset=MenuCatalog.objects.filter(
                    is_hidden=False,
                    type_menu_id__in=VALID_SIMILAR_TYPE_IDS # Types pour le contenu des onglets
                ).exclude(
                    id=UNCATEGORIZED_CATEGORY_ID if UNCATEGORIZED_CATEGORY_ID else -1 # Exclut si défini
                ).order_by('order_number', 'name').prefetch_related(
                    # Optionnel : Précharger le Niveau 3 si nécessaire
                    Prefetch(
                        'menucatalog_set',
                        queryset=MenuCatalog.objects.filter(is_hidden=False, type_menu_id__in=VALID_SIMILAR_TYPE_IDS).exclude(id=UNCATEGORIZED_CATEGORY_ID if UNCATEGORIZED_CATEGORY_ID else -1).order_by('order_number', 'name'),
                        to_attr='cached_children' # Pour les petits-enfants
                    )
                ),
                to_attr='cached_children' # Enfants directs des onglets
            )
        )
        logger.debug(f"Found {menu_tabs_items.count()} items for menu tabs under '{catalog_root.name}'.")

    except Exception as e:
        logger.error(f"Error fetching menu items for dropdown: {e}", exc_info=True)
        return HttpResponse("<p>Ошибка загрузки данных меню.</p>", status=500)

    context = {
        'menu_tabs_items': menu_tabs_items # Renommé pour clarté dans le partial
    }
    html_content = render_to_string('includes/partials/_menu_dropdown_content.html', context)
    return HttpResponse(html_content)





class IndexView(TemplateView):
    template_name = "catalog/index.html"

    def get(self, request):
        
        is_index = True

        #Set unique key for cache definition
        cache_key_hits = 'main_page_product_hits'
        cache_time = 60 * 30

        promo_list_main = Promo.objects.filter(is_show_main=True, is_hidden=False)[:SIZE_OFFERS_INDEX]

        categories_list = MenuCatalog.objects.filter(type_menu_id__in=[6, 7, 8], is_hidden=False, flag_main=True).exclude(id=2)[:SIZE_SALE_INDEX]

        # Get hit from cache
        hit_products = cache.get(cache_key_hits)
        if hit_products is None:
            hit_products = Product.objects.filter(
                is_hit=True,
                is_hidden=False
            ).select_related('catalog').only(
                'id',
                'title',
                'slug',
                'image',
                'price',
                'catalog__name',
                'catalog__slug', 
            ).order_by('-created_at')[:10]

            cache.set(cache_key_hits, hit_products, cache_time)

        

        context = {
            'categories_list':categories_list,
            'is_index' : True,
            'hit_products':hit_products,
            'promo_list_main':promo_list_main,
        }

        return render(request, self.template_name, context)
    


# --- Vue Principale Catégorie/Liste ---
class MenuView(View):
    """Affiche la page catégorie/liste produit initiale avec les filtres."""
    # template_name est défini par type_menu de current_menu
    template_name = 'catalog/catalog.html'

    def get(self, request, hierarchy, filter_segment=None):
        logger.debug(f"MenuView GET. Hierarchy: '{hierarchy}', Filter segment: '{filter_segment}'")

        #Variable initialisation
        service_list = []
        promo_list = []

        # --- Extraction chemin catégorie ---
        hierarchy_path = hierarchy
        slugs = hierarchy_path.strip('/').split('/')
        current_slug = slugs[-1]
        target_item = None
        try:
            target_item = MenuCatalog.objects.select_related('parent', 'type_menu').get(slug=current_slug, is_hidden=False)
            ancestors = target_item.get_ancestors(include_self=True)
            candidate_slugs = [slugify(unidecode(a.slug or f"cat-{a.id}")) for a in ancestors] # Utilise unidecode
            if candidate_slugs != slugs:
                logger.warning(f"Path mismatch for slug '{current_slug}'. Expected '{'/'.join(candidate_slugs)}', got '{hierarchy_path}'. Raising 404.")
                raise Http404("Category path mismatch or inactive")
        except MenuCatalog.DoesNotExist:
            raise Http404("Category not found")
        except MenuCatalog.MultipleObjectsReturned:
            # Gérer le cas où le slug final n'est pas unique globalement
            # (Nécessite une logique find_by_full_path robuste)
            logger.error(f"Multiple categories found with slug '{current_slug}'. This should ideally not happen if slugs are unique per level or globally.")
            raise Http404("Ambiguous category slug")

        current_menu = target_item
        
        # --- Interdire l'accès à la catégorie non classée ---
        if str(current_menu.id) == UNCATEGORIZED_CATEGORY_ID:
            logger.warning(f"Attempt to access Uncategorized Category page directly: ID {current_menu.id}, Slug {current_menu.slug}")
            raise Http404("Cette catégorie n'est pas accessible directement.")
        
        # --- Parser les filtres de l'URL ---
        active_filters_dict = parse_filters_from_url(filter_segment)
        logger.debug(f"Initial active_filters_dict from URL: {active_filters_dict}")

        # --- Queryset de base produits ---
        base_product_qs = Product.objects.filter(catalog=current_menu,is_hidden=False).select_related('catalog')

        # --- 1. Appliquer les filtres de l'URL aux produits ---
        #     On travaille sur une copie pour le calcul des filtres disponibles
        filtered_products_for_display = apply_filters_to_queryset(base_product_qs.all(), active_filters_dict)
        # Appliquer le filtre 'available' ici si on ne veut afficher que les disponibles
        filtered_products_for_display = filtered_products_for_display
        logger.debug(f"Count after M2M filters & 'available' (initial load): {filtered_products_for_display.count()}")

        # --- 2. Récupérer les filtres disponibles BASÉS sur les produits de la catégorie AVANT filtrage M2M ---
        #    pour montrer toutes les options possibles pour cette catégorie.
        #    Les comptes refléteront le nombre de produits DANS LE QUERSET NON FILTRÉ PAR M2M.
        available_filters_data = current_menu.get_available_filters_data(base_product_queryset=filtered_products_for_display)
        logger.debug(f"Available filters data (based on all available products in category): {available_filters_data}")

        # --- Tri (appliqué au queryset déjà filtré par M2M et 'available') ---
        sort_type = request.GET.get('sort')
        sort_type_str, sorted_product_qs = get_sort_type(sort_type, filtered_products_for_display)


        # --- Construire la chaîne des filtres actifs pour l'affichage ---
        # On peut passer les FilterCategory déjà connues pour optimiser
        active_filter_categories_in_view = FilterCategory.objects.filter(
            slug__in=active_filters_dict.keys(), is_active=True
        )
        active_filters_display = get_active_filters_display_string(
            active_filters_dict,
            filter_categories_qs=active_filter_categories_in_view 
        )
        # -------------------------------------------------------------
        # Gestion de la liste "uslugi"
        if current_menu and current_menu.slug == "uslugi":
            try:
                service_list = Uslugi.objects.filter(is_hidden=False).only('id', 'name','image','description',).order_by('order_number')[:MAX_ITEM]
            except ImportError:
                logger.error("Could not import Uslugi model. 'services' app configured?")
                service_list = []
            except Exception as e_uslugi:
                logger.error(f"Error fetching Uslugi: {e_uslugi}")
                service_list = []

        # Gestion de la liste "promo"
        if current_menu and current_menu.slug == "akcii":
            try:
                promo_list= Promo.objects.filter(is_hidden=False).only('id', 'name','image','description','text').order_by('order_number')[:MAX_ITEM]
            except ImportError:
                logger.error("Could not import Promo model. 'promo' app configured?")
                promo_list = []
            except Exception as e_promo:
                logger.error(f"Error fetching Uslugi: {e_promo}")
                promo_list = []


        similar_categories_list = get_similar_categories_optimized(current_menu, min_results=6)

        str_filter_name = current_menu.name

        # --- Pagination ---
        product_list_count = sorted_product_qs.count() # Compte final
        paginator = Paginator(sorted_product_qs, PRODUCTS_PER_PAGE)
        page_number_str = request.GET.get('page', '1')
        try: page_number = int(page_number_str); page_number = max(1, page_number)
        except: page_number = 1

        try:
            current_page_products = paginator.page(page_number)
        except EmptyPage:
            current_page_products = paginator.page(paginator.num_pages if paginator.num_pages > 0 else 1)
        except PageNotAnInteger:
            current_page_products = paginator.page(1)


        # --- Calcul Plage Pagination ---
        paginator_range = [] # Initialise avec le bon nom
        if paginator.num_pages > 1:
            on_each_side = 2
            on_ends = 1
            num_pages = paginator.num_pages
            current_page_num_in_paginator = current_page_products.number

            if num_pages <= (on_each_side + on_ends) * 2:
                # Utilise paginator.page_range qui est un itérable de numéros de page
                paginator_range = list(paginator.page_range)
            else:
                # Pages du début
                paginator_range.extend(range(1, on_ends + 1))
                # Ellipse si nécessaire
                if current_page_num_in_paginator > on_each_side + on_ends + 1:
                    paginator_range.append(None) # Représente '...'
                # Pages autour de la page actuelle
                start_mid = max(on_ends + 1, current_page_num_in_paginator - on_each_side)
                end_mid = min(num_pages - on_ends, current_page_num_in_paginator + on_each_side)
                paginator_range.extend(range(start_mid, end_mid + 1))
                # Ellipse si nécessaire
                if current_page_num_in_paginator < num_pages - on_ends - on_each_side:
                    paginator_range.append(None) # Représente '...'
                # Pages de la fin
                paginator_range.extend(range(num_pages - on_ends + 1, num_pages + 1))
        # -------------------------------------------------------------------

        context = {
            'current_menu': current_menu,
            'str_filter_name':str_filter_name,
            'product_list': current_page_products,
            'product_list_count': product_list_count,
            'ancestors': ancestors,
            'service_list':service_list,
            'promo_list':promo_list,
            'similar_categories':similar_categories_list,
            'available_filters': available_filters_data,
            'active_filters_dict': active_filters_dict,
            'base_category_url': current_menu.get_absolute_url(),
            'request': request,
            'sort_type': sort_type,
            'sort_type_str': sort_type_str,
            'paginator_range': paginator_range,
            'current_page_number': current_page_products.number,
            'total_pages': paginator.num_pages,
            'active_filters_display': active_filters_display,
        }

        template_to_render = self.template_name # Fallback
        # --- Logique de template dynamique ---
        if hasattr(current_menu, 'type_menu') and current_menu.type_menu and current_menu.type_menu.template:
            # S'assure que current_menu.type_menu.template est un chemin de template valide
            if isinstance(current_menu.type_menu.template, str) and current_menu.type_menu.template.endswith('.html'):
                template_to_render = current_menu.type_menu.template
            else:
                logger.warning(f"Invalid template path for MenuCatalog {current_menu.id} TypeMenu: {current_menu.type_menu.template}. Using default.")
        else:
            logger.debug(f"No specific template for MenuCatalog {current_menu.id}. Using default: {template_to_render}")
        # -----------------------------------

        return render(request, template_to_render, context)


# class ProductView(TemplateView):
#     """ Class for displaying the product page """
#     template_name = "catalog/product.html"

#     def get(self, request, product_slug):
#         product = get_object_or_404(Product, slug=product_slug)
#         current_menu = product.catalog
        
#         similar_products = get_similar_products(product, max_results=6) 
        
        
#         str_filter_name = current_menu.name

#         context = {
#             'current_menu':current_menu,
#             'product':product,
#             'similar_products': similar_products,
#             'str_filter_name':str_filter_name,
#         }

#         return render(request, self.template_name, context)

class ProductView(View):
    template_name = 'catalog/product.html'

    def get(self, request, product_slug):
        
        product = get_object_or_404(
            Product.objects.select_related('catalog__type_menu'),
            slug=product_slug,
            is_hidden=False
        )

        # --- Interdire produits de la catégorie non classée ---
        if product.catalog and str(product.catalog.id) == UNCATEGORIZED_CATEGORY_ID:
            logger.warning(f"Attempt to access product '{product.slug}' from Uncategorized Category ID {product.catalog.id}")
            raise Http404("Товар не найден или не доступен в этой категории.")
        # ----------------------------------------------------------------------------

        current_menu = product.catalog 

        # ---  Produits Similaires ---
        similar_products = get_similar_products(product, max_results=6)
        # ---------------------------------------------------

        str_filter_name = current_menu.name

        context = {
            'product': product,
            'current_menu': current_menu,
            'similar_products': similar_products,
            'str_filter_name':str_filter_name,
        }
        return render(request, self.template_name, context)    



# --- Vue AJAX POUR FILTRER ---

class FilterProductsView(View):
    partial_template_name = 'includes/partials/product_list_items.html'
    filters_partial_template_name = 'includes/partials/_filters_partial.html'
    pagination_partial_template_name = 'includes/partials/_pagination_partial.html' # Nouveau

    def get(self, request, *args, **kwargs):
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'AJAX only'}, status=400)

        category_slug = request.GET.get('category_slug')
        # --- RÉCUPÉRER page et sort ---
        sort_type = request.GET.get('sort')
        page_number_str = request.GET.get('page', '1')
        try: page_number = int(page_number_str); page_number = max(1, page_number)
        except: page_number = 1
        # -----------------------------

        if not category_slug: return JsonResponse({'error': 'Missing category slug'}, status=400)
        try: current_category = get_object_or_404(MenuCatalog, slug=category_slug, is_hidden=False)
        except Http404: return JsonResponse({'error': 'Category not found'}, status=404)

        logger.debug(f"AJAX Filter/Sort/Page: Cat='{category_slug}', Page={page_number}, Sort='{sort_type}', Filters={request.GET}")

        # 1. Parser filtres actifs
        active_filters_dict = parse_filters_from_request(request.GET)

        # 2. Queryset de base
        base_product_qs = Product.objects.filter(catalog=current_category, is_hidden=False).select_related('catalog')

        # 3. Appliquer filtres actifs
        filtered_product_qs = apply_filters_to_queryset(base_product_qs.all(), active_filters_dict) # Utilise .all() pour copie

        # 4. Recalculer filtres disponibles (pour les comptes)
        available_filters_data = current_category.get_available_filters_data(base_product_queryset=filtered_product_qs)

        # --- 5. Appliquer le tri ---
        sort_type_str, sorted_product_qs = get_sort_type(sort_type, filtered_product_qs)
        # ---------------------------

        # --- 6. Construire la chaîne des filtres actifs pour l'affichage ---
        #    (Identique à MenuView)
        active_filter_categories_in_view = FilterCategory.objects.filter(
            slug__in=active_filters_dict.keys(), is_active=True
        )
        active_filters_display = get_active_filters_display_string(
            active_filters_dict,
            filter_categories_qs=active_filter_categories_in_view
        )

        print(active_filters_display)
        # -------------------------------------------------------------
        # 7. Compter et Paginer
        product_list_count = sorted_product_qs.count() # Compte final
        paginator = Paginator(sorted_product_qs, PRODUCTS_PER_PAGE)
        try: products_page = paginator.page(page_number)
        except EmptyPage: products_page = paginator.page(paginator.num_pages if paginator.num_pages > 0 else 1)

        # --- 8. Calculer la plage de pagination pour le partial ---
        paginator_range = []
        if paginator.num_pages > 1:
            on_each_side = 2; on_ends = 1; num_pages = paginator.num_pages
            current_page_num = products_page.number
            if num_pages <= (on_each_side + on_ends) * 2: paginator_range = paginator.page_range
            else:
                paginator_range.extend(range(1, on_ends + 1))
                if current_page_num > on_each_side + on_ends + 1: paginator_range.append(None)
                start_mid = max(on_ends + 1, current_page_num - on_each_side)
                end_mid = min(num_pages - on_ends, current_page_num + on_each_side)
                paginator_range.extend(range(start_mid, end_mid + 1))
                if current_page_num < num_pages - on_ends - on_each_side: paginator_range.append(None)
                paginator_range.extend(range(num_pages - on_ends + 1, num_pages + 1))
        # --------------------------------------------------------

        # 9. Rendre les templates partiels
        context_products = {
            'product_list': products_page, 
            'request': request
        } 
        html_products = render_to_string(self.partial_template_name, context_products, request=request)

        context_filters = { 
            'available_filters': available_filters_data, 
            'active_filters_dict': active_filters_dict,
            'current_menu': current_category, 
            'base_category_url': current_category.get_absolute_url(),
            'request': request 
        }
        html_filters = render_to_string(self.filters_partial_template_name, context_filters)

        # --- Rendu du partial de pagination ---
        context_pagination = {
            'product_list': products_page, # Passe l'objet Page
            'search_text': '', # Vide pour les catégories, sera request.GET.search pour la recherche
            'paginator_range': paginator_range,
            'current_category_url_no_filters': current_category.get_absolute_url(), # Pour construire les liens
            'active_filters_for_url': build_filter_url_segment(active_filters_dict), # Ex: f/cat=val/
            'current_sort_for_url': sort_type or '', # Ex: price_asc
            'request': request,
        }
        html_pagination = render_to_string(self.pagination_partial_template_name, context_pagination)
        # -----------------------------------

        # 10. Construire l'URL pour pushState
        base_url = current_category.get_absolute_url()
        filter_segment = build_filter_url_segment(active_filters_dict)
        final_new_url_path = base_url
        if filter_segment:
            if not final_new_url_path.endswith('/'): final_new_url_path += '/'
            final_new_url_path += filter_segment

        query_params_for_pushstate = {}
        # Ajoute 'page' seulement si > 1
        if products_page.number > 1: query_params_for_pushstate['page'] = products_page.number
        # Ajoute 'sort' seulement s'il est défini
        if sort_type: query_params_for_pushstate['sort'] = sort_type

        query_string_for_pushstate = urllib.parse.urlencode(query_params_for_pushstate)
        final_new_url = final_new_url_path + (f"?{query_string_for_pushstate}" if query_string_for_pushstate else "")

        # 11. Construire la réponse JSON
        response_data = {
            'html_products': html_products,
            'html_filters': html_filters,
            'html_pagination': html_pagination, # Ajout du HTML pagination
            'product_count': product_list_count,
            'has_next_page': products_page.has_next(), # Renommé pour clarté
            'next_page_number': products_page.next_page_number() if products_page.has_next() else None,
            'total_pages': paginator.num_pages, # <--- AJOUTER CETTE LIGNE
            'current_page_number': products_page.number, # Pour mettre à jour le bouton Load More
            'active_filters_display': active_filters_display, # <--- AJOUT À LA RÉPONSE JSON
            'new_url': final_new_url,
        }
        return JsonResponse(response_data)

