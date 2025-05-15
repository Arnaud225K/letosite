# from django.shortcuts import render
# from django.views.generic.base import TemplateView
# from django.db.models import Q
# from django.urls import reverse
# from django.db.models import Count
# from django.shortcuts import get_object_or_404
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# from filials.views import get_current_filial
# from menu.models import Product, MenuCatalog
# from .models import SearchTerm, SearchChange

# from django.template.loader import render_to_string
# from django.http import JsonResponse
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, Page


# PRODUCTS_PER_PAGE = 12


# class SearchView(TemplateView):
#     template_name = "search/results.html"

#     def get(self, request):
#         search_text = request.GET.get('search', '')
#         current_url_search = f"{reverse('search:results')}?search={search_text.replace(' ', '+')}"
        
#         # Handle AJAX requests for pagination
#         page_number = request.GET.get('page', '')
#         is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

#         # Log search term if it's not an AJAX request
#         if not page_number:
#             self.log_search_term(search_text, request)

#         words = _prepare_words(search_text)
#         search_filter = self.build_search_filter(words)

#         #Fetch products based on filters
#         product_list = Product.objects.filter(search_filter, is_hidden=False, catalog__is_hidden=False).exclude(catalog__id=2).only('title', 'slug')
        
#         # paginator = Paginator(product_list, COUNT_ITEM_PAGE)
#         # page_obj = paginator.get_page(page_number)

#         paginator = Paginator(product_list, PRODUCTS_PER_PAGE)

#         try:
#             current_page_products = paginator.page(1)
#         except EmptyPage:
#             current_page_products = Page([], 1, paginator)

#         # Prepare context for rendering including available filters:
#         context = {
#             'search_text': search_text,
#             'product_list': current_page_products,
#             'current_url_search': current_url_search,
#             'product_list_count': product_list.count(),
#             # 'ajax_load_url': reverse('menu:ajax_load_more', kwargs={'category_slug': current_url_search}), 
#         }

#         return render(request, self.template_name, context)

#     def log_search_term(self, search_text, request):
#         current_filial = get_current_filial(request)
#         x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#         if x_forwarded_for:
#             ip_address = x_forwarded_for.split(',')[0]
#         else:
#             ip_address = request.META.get('REMOTE_ADDR')
        
#         SearchTerm.objects.create(
#             q=search_text,
#             filial_name=current_filial.name,
#             subdomain_name=current_filial.subdomain_name,
#             ip_address=ip_address
#         )

#     def build_search_filter(self, words):
#         search_filter = Q()
#         for word in words:
#             word = word.replace(',', '.')
#             synonyms = SearchChange.objects.filter(source=word).values_list('result', flat=True)
#             search_filter |= Q(title__icontains=word) | Q(title__in=synonyms)
        
#         return search_filter

# def _prepare_words(search_text):
#     STRIP_WORDS = {'a', 'an', 'and', 'by', 'for', 'from', 'in', 'no', 
#                 'not','of','on','or','that','the','to','with'}
#     return [word for word in search_text.split() if word not in STRIP_WORDS][:15]

# menu/views.py (ou search/views.py)

from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.http import Http404, JsonResponse
from .models import SearchTerm, SearchChange, SearchRemove
from menu.models import Product, MenuCatalog

from filials.views import get_current_filial
from django.conf import settings
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

PRODUCTS_PER_PAGE = 12
# ID Catégorie Non Classé (depuis settings ou constante)
UNCATEGORIZED_CATEGORY_ID = getattr(settings, 'UNCATEGORIZED_CATEGORY_ID', '2')

# # Mots vides courants + potentiellement ceux de la DB
# # On charge les mots à retirer une seule fois au démarrage (ou via cache)
# try:
#     # Récupère les mots depuis SearchRemove et les ajoute au set
#     DB_STRIP_WORDS = set(SearchRemove.objects.values_list('str_remove', flat=True))
#     logger.info(f"Loaded {len(DB_STRIP_WORDS)} strip words from database.")
# except Exception as e_strip:
#     logger.warning(f"Could not load strip words from DB: {e_strip}. Using default set.")
#     DB_STRIP_WORDS = set()

# DEFAULT_STRIP_WORDS = {'a', 'an', 'and', 'by', 'for', 'from', 'in', 'no',
#                         'not','of','on','or','that','the','to','with'}
# ALL_STRIP_WORDS = DEFAULT_STRIP_WORDS.union(DB_STRIP_WORDS)


# def _prepare_words(search_text):
#     """Nettoie et prépare les mots pour la recherche, exclut les mots vides."""
#     if not search_text:
#         return []
#     words = search_text.lower().split() # Met en minuscule
#     prepared = [word for word in words if word not in ALL_STRIP_WORDS and len(word) > 1] # Exclut mots vides et trop courts
#     logger.debug(f"Prepared search words: {prepared[:15]}")
#     return prepared[:15] # Limite à 15 mots


# class SearchView(TemplateView):
#     template_name = "search/results.html"
#     # template_name_partial = "search/partials/results_items.html" # Pour AJAX futur

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         search_text = self.request.GET.get('search', '').strip()
#         context['search_text'] = search_text

#         if not search_text:
#             context['products'] = Product.objects.none()
#             context['product_list_count'] = 0
#             return context

#         # Log la recherche seulement si ce n'est pas une requête AJAX de pagination
#         is_ajax_pagination = self.request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 'page' in self.request.GET
#         if not is_ajax_pagination:
#             self.log_search_term(search_text, self.request)

#         words = _prepare_words(search_text)
#         if not words:
#             context['products'] = Product.objects.none()
#             context['product_list_count'] = 0
#             return context

#         # --- Construction Optimisée du Filtre ---
#         search_filter = self.build_search_filter_optimised(words)
#         # -------------------------------------

#         # --- Requête Principale Optimisée ---
#         base_qs = Product.objects.filter(
#             is_hidden=False,
#             catalog__is_hidden=False # Jointure implicite
#         ).exclude(
#             catalog__id=UNCATEGORIZED_CATEGORY_ID
#         )

#         # Applique le filtre de recherche
#         product_list = base_qs.filter(search_filter).distinct() # distinct() important si OR ou FTS

#         # --- Fin Requête Principale ---

#         product_list_count = product_list.count() # Compte après filtrage

#         # --- Pagination ---
#         paginator = Paginator(product_list, PRODUCTS_PER_PAGE)
#         page_number = self.request.GET.get('page', 1)
#         try:
#             current_page_products = paginator.page(page_number)
#         except EmptyPage:
#             # Si page invalide (ex: > max), retourne la dernière page
#             current_page_products = paginator.page(paginator.num_pages)
#         except PageNotAnInteger:
#             current_page_products = paginator.page(1)




#         # --- Calcul de la Plage de Pagination à Afficher ---
#         # Ex: Affiche 2 pages avant et 2 après la page actuelle, plus première/dernière
#         on_each_side = 2
#         on_ends = 1
#         num_pages = paginator.num_pages
#         current_page_num = current_page_products.number

#         if num_pages <= (on_each_side + on_ends) * 2: # Si peu de pages, les afficher toutes
#             page_range = paginator.page_range
#         else:
#             page_range = []
#             # Pages du début
#             page_range.extend(range(1, on_ends + 1))
#             # Ellipse si nécessaire
#             if current_page_num > on_each_side + on_ends + 1:
#                 page_range.append(None) # Représente '...'
#             # Pages autour de la page actuelle
#             start_mid = max(on_ends + 1, current_page_num - on_each_side)
#             end_mid = min(num_pages - on_ends, current_page_num + on_each_side)
#             page_range.extend(range(start_mid, end_mid + 1))
#             # Ellipse si nécessaire
#             if current_page_num < num_pages - on_ends - on_each_side:
#                  page_range.append(None) # Représente '...'
#             # Pages de la fin
#             page_range.extend(range(num_pages - on_ends + 1, num_pages + 1))

#         context['paginator_range'] = page_range
#         # ----------------------------------------------------

#         context['product_list'] = current_page_products # Objet Page
#         context['product_list_count'] = product_list_count
#         # Optionnel: passer l'URL de recherche courante pour la pagination AJAX future
#         context['current_search_url'] = self.request.get_full_path()

#         # Si requête AJAX pour pagination, ne renvoyer que le partiel
#         # if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         #    self.template_name = self.template_name_partial # Change le template

#         return context

#     def log_search_term(self, search_text, request):
#         # ... (votre logique de log existante, inchangée) ...
#         current_filial = get_current_filial(request)
#         ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
#         try:
#             SearchTerm.objects.create(
#                 q=search_text[:512],
#                 filial_name=current_filial.name if current_filial else 'Unknown',
#                 subdomain_name=current_filial.subdomain_name if current_filial else None,
#                 ip_address=ip_address
#             )
#         except Exception as e_log:
#             logger.error(f"Failed to log search term '{search_text}': {e_log}")


#     def build_search_filter_optimised(self, words):
#         """Construit le filtre Q basé sur les mots et leurs synonymes (logique AND)."""
#         if not words:
#             return Q() # Retourne un filtre vide si pas de mots

#         # 1. Récupérer tous les synonymes pertinents en une seule requête
#         synonyms_map = defaultdict(list)
#         synonym_qs = SearchChange.objects.filter(source__in=words).values('source', 'result')
#         for item in synonym_qs:
#             synonyms_map[item['source']].append(item['result'])

#         # 2. Construire un filtre Q complexe avec AND pour chaque mot source
#         final_filter = Q() # Commence avec un filtre vide (AND)

#         for word in words:
#             # Inclut le mot original ET ses synonymes dans la recherche pour CE mot
#             search_terms_for_word = {word} | set(synonyms_map.get(word, []))
#             logger.debug(f"Search terms for '{word}': {search_terms_for_word}")

#             # Crée un filtre OR pour ce mot et ses synonymes
#             word_filter = Q()
#             for term in search_terms_for_word:
#                 # Utilise title__icontains pour chaque terme (peut être lent)
#                 word_filter |= Q(title__icontains=term)
#                 # --- OPTION Recherche Full-Text (Beaucoup plus rapide si configurée) ---
#                 # Nécessite un SearchVectorField sur le modèle et une config DB
#                 # from django.contrib.postgres.search import SearchQuery
#                 # word_filter |= Q(search_vector=SearchQuery(term, config='russian')) # Exemple PostgreSQL
#                 # -------------------------------------------------------------------

#             # Combine le filtre de ce mot avec le filtre global en utilisant AND
#             final_filter &= word_filter

#         return final_filter

#     # --- Fonction originale (gardée pour comparaison si besoin) ---
#     # def build_search_filter_original(self, words):
#     #     search_filter = Q() # Commence vide (OR)
#     #     for word in words:
#     #         # word = word.replace(',', '.') # Déplacer le nettoyage dans _prepare_words si besoin
#     #         # Requête DB dans la boucle !
#     #         synonyms = SearchChange.objects.filter(source=word).values_list('result', flat=True)
#     #         # Combine avec OR
#     #         search_filter |= Q(title__icontains=word) | Q(title__in=list(synonyms)) # list() est important si queryset vide
#     #     return search_filter


# # --- Fonctions auxiliaires ---
# # get_current_filial(request) doit être définie ou importée


try:
    DB_STRIP_WORDS = set(SearchRemove.objects.values_list('str_remove', flat=True))
except Exception: DB_STRIP_WORDS = set()
DEFAULT_STRIP_WORDS = {'a','an','and','by','for','from','in','no','not','of','on','or','that','the','to','with'}
ALL_STRIP_WORDS = DEFAULT_STRIP_WORDS.union(DB_STRIP_WORDS)

def _prepare_words(search_text):
    if not search_text: return []
    words = search_text.lower().split()
    prepared = [word for word in words if word not in ALL_STRIP_WORDS and len(word) > 1]
    return prepared[:15]

# --- Fonction de log (inchangée en interne) ---
def log_search_term(search_text, request):
    if not search_text: # Ne pas logger les recherches vides
        return
    current_filial = get_current_filial(request) # Assurez-vous que cette fonction est robuste
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
    try:
        # Optionnel: Vérifier si un log très récent existe déjà pour cette session/IP/terme ?
        # Ceci est plus complexe et peut ne pas être nécessaire.
        SearchTerm.objects.create(
            q=search_text[:512],
            filial_name=current_filial.name if current_filial and hasattr(current_filial, 'name') else 'Unknown',
            subdomain_name=current_filial.subdomain_name if current_filial and hasattr(current_filial, 'subdomain_name') else None,
            ip_address=ip_address,
            path_site=request.path_info # Ajoute la page actuelle
        )
        logger.info(f"Search term logged: '{search_text}' from IP: {ip_address}")
    except Exception as e_log:
        logger.error(f"Failed to log search term '{search_text}': {e_log}")

# --- Fonction de construction du filtre (simplifiée pour synonymes seulement) ---
def build_search_filter_with_synonyms(words):
    """Construit le filtre Q basé sur les mots et leurs synonymes DB (logique AND)."""
    if not words: return Q()

    # 1. Récupérer synonymes DB (bidirectionnel)
    synonyms_map = defaultdict(set) # Utilise un set pour éviter doublons de synonymes
    potential_sources = set(words)
    synonym_qs = SearchChange.objects.filter(
        Q(source__in=potential_sources) | Q(result__in=potential_sources)
    ).values('source', 'result')

    for item in synonym_qs:
        # Ajoute les relations dans les deux sens
        synonyms_map[item['source']].add(item['result'])
        synonyms_map[item['result']].add(item['source'])

    # 2. Construire le filtre final (AND entre les mots)
    final_filter = Q()
    for word in words:
        # Inclut le mot original ET ses synonymes DB
        search_terms_for_word = {word} # Commence avec le mot original
        search_terms_for_word.update(synonyms_map.get(word, set())) # Ajoute synonymes
        # Cherche aussi si le mot est un RESULTAT d'un synonyme
        for src, results in synonyms_map.items():
            if word in results:
                search_terms_for_word.add(src)


        logger.debug(f"Final search terms for '{word}': {search_terms_for_word}")

        # Crée un filtre OR pour ce mot et ses synonymes/formes associées
        word_filter = Q()
        # --- Recherche Full-Text reste RECOMMANDÉE ---
        # if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
        #      # ... (Logique FTS avec " | ".join(search_terms_for_word)) ...
        # else: # Fallback icontains
        for term in search_terms_for_word:
            word_filter |= Q(title__icontains=term)
            # Optionnel : Chercher aussi dans le SKU ?
            # word_filter |= Q(sku__icontains=term)
            # Optionnel : Chercher aussi dans la description ? (peut être lent sans FTS)
            # word_filter |= Q(description__icontains=term)
        # --- Fin Fallback ---

        # Combine avec AND
        if word_filter: # N'ajoute que s'il y a des termes à chercher pour ce mot
            final_filter &= word_filter
        else: # Si un mot n'a aucun terme (très rare), on pourrait retourner Q(pk=None) pour aucun résultat
            logger.warning(f"No search terms generated for word '{word}', search might yield no results if AND logic is strict.")
            # return Q(pk=None) # Option stricte

    return final_filter


# --- Vue Principale ---
class SearchView(TemplateView):
    template_name = "search/results.html"

    def get(self, request, *args, **kwargs):
        search_text = request.GET.get('search', '').strip()
        page_number_str = request.GET.get('page', '1') # Récupère comme chaîne
        context = {'search_text': search_text}

        # --- Conversion et validation numéro de page ---
        try:
            page_number = int(page_number_str)
            if page_number < 1: page_number = 1
        except ValueError:
            page_number = 1 # Défaut à 1 si non numérique
        # -------------------------------------------

        is_pagination_request = page_number > 1 # Vrai si page > 1
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if search_text and not is_pagination_request and not is_ajax:
            log_search_term(search_text, request)

        product_list = Product.objects.none()
        product_list_count = 0
        paginator = None # Initialise
        current_page_products = None # Initialise

        if search_text:
            words = _prepare_words(search_text)
            if words:
                search_filter = build_search_filter_with_synonyms(words)
                base_qs = Product.objects.filter(
                    is_hidden=False, catalog__is_hidden=False
                ).exclude(catalog__id=UNCATEGORIZED_CATEGORY_ID)

                product_list = base_qs.filter(search_filter).distinct().select_related('catalog').only(
                    'id', 'title', 'slug', 'image', 'price',
                    'catalog__name'
                )
                try:
                    product_list_count = product_list.count()
                except Exception: product_list_count = 0

        # --- Pagination ---
        if product_list_count > 0: # Crée le paginator seulement s'il y a des résultats
            paginator = Paginator(product_list, PRODUCTS_PER_PAGE)
            try:
                current_page_products = paginator.page(page_number)
            except EmptyPage:
                # Si la page demandée est hors limites, retourne la dernière page
                current_page_products = paginator.page(paginator.num_pages)
            # PageNotAnInteger est déjà géré par le int() et le défaut à 1 plus haut
        else:
            # Crée un objet Page vide si aucun résultat
            paginator = Paginator([], PRODUCTS_PER_PAGE) # Paginator vide
            current_page_products = paginator.page(1) # Page 1 vide

        # --- Calcul Plage Pagination (inchangé) ---
        page_range = []
        if paginator and paginator.num_pages > 1:
            on_each_side = 2; on_ends = 1; num_pages = paginator.num_pages
            current_page_num = current_page_products.number
            if num_pages <= (on_each_side + on_ends) * 2: page_range = paginator.page_range
            else:
                page_range.extend(range(1, on_ends + 1))
                if current_page_num > on_each_side + on_ends + 1: page_range.append(None)
                start_mid = max(on_ends + 1, current_page_num - on_each_side)
                end_mid = min(num_pages - on_ends, current_page_num + on_each_side)
                page_range.extend(range(start_mid, end_mid + 1))
                if current_page_num < num_pages - on_ends - on_each_side: page_range.append(None)
                page_range.extend(range(num_pages - on_ends + 1, num_pages + 1))
        # -----------------------------------------

        context['product_list'] = current_page_products # Objet Page
        context['product_list_count'] = product_list_count
        context['paginator_range'] = page_range
        # --- Ajout pour le titre ---
        context['current_page_number'] = current_page_products.number
        context['total_pages'] = paginator.num_pages if paginator else 0
        # --------------------------

        return render(request, self.template_name, context)

    # La méthode get_context_data n'est plus nécessaire si tout est fait dans get()
    # def get_context_data(self, **kwargs): ...