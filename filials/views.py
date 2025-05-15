from django.shortcuts import render
from .models import Filials
from django.views.generic.base import TemplateView

from letosite import settings

import logging # Import logging

# Configurez le logger (bonne pratique)
logger = logging.getLogger(__name__)



# def get_current_filial(request):
# 	"""
# 	:param current_host: Хост
# 	:return:current_filial: Текущий филиал
# 	 Функция определяет текущий филиал
# 	"""
# 	# Определение города по ip
# 	user_filial = None
# 	city_ip = None
# 	host = request.get_host()
# 	try:
# 		user_filial = request.session['current_filial_flag']
# 	except:
# 		pass
# 	# анализ поддомена и выбор города
# 	current_filial = None
# 	current_filial_ip = None
# 	filials = Filials.objects.filter(isHidden=False).only('id', 'name', 'subdomain_name', 'is_main', 'comment')
# 	if filials:
# 		current_filial = filials.filter(is_main=True).first()
# 		if not current_filial:
# 			current_filial = filials.first()
# 		for item in filials:
# 			if item.subdomain_name and item.subdomain_name + 'indusite.kz' == host:
# 				current_filial = item
# 			if not user_filial:
# 				if item.name == city_ip:
# 					current_filial_ip = item
		
# 		# Если выбран поддомен, то выбор города не работает
# 		if not current_filial.subdomain_name:
# 			if (not (user_filial or current_filial_ip)) and filials:
# 				current_filial_ip = filials.first()
# 			if not user_filial and current_filial_ip:
# 				request.session['current_filial_flag'] = current_filial_ip.id
# 		else:
# 			current_filial_ip = None
		
# 		current_filial = Filials.objects.get(id=current_filial.id)
# 	else:
# 		current_filial = Filials()
# 	return current_filial


# FILIALS_CACHE_KEY = 'all_active_filials_structured_v3'
# FILIALS_CACHE_TIMEOUT = 60 * 60 # 1 heure

# def _get_structured_filials_data_from_cache_or_db():
#     """
#     Récupère les données structurées des filiales actives depuis le cache ou la DB.
#     IGNORE le cache et va TOUJOURS à la DB si settings.DEBUG est True.
#     """
#     # --- Modification ici : Vérifie settings.DEBUG ---
#     if not settings.DEBUG: # N'utilise le cache que si on N'EST PAS en mode DEBUG
#         cached_data = cache.get(FILIALS_CACHE_KEY)
#         if cached_data is not None:
#             # print(f"CACHE HIT: Filials key '{FILIALS_CACHE_KEY}'") # Débogage
#             return cached_data
#         # else:
#             # print(f"CACHE MISS: Filials key '{FILIALS_CACHE_KEY}'") # Débogage
#     # else:
#         # print(f"DEBUG MODE: Bypassing cache for Filials.") # Débogage

#     # --- Le reste de la logique de récupération DB est exécuté si DEBUG=True ou si le cache est manquant ---
#     structured_data = {
#         'by_id': {},
#         'by_subdomain': {},
#         'main_id': None,
#         'first_id': None,
#     }

#     try:
#         filials_queryset = Filials.objects.filter(isHidden=False).only(
#             'id', 'name', 'subdomain_name', 'is_main'
#         ).order_by('pk')

#         first_filial_pk = None

#         for filial in filials_queryset:
#             filial_id_str = str(filial.id)
#             subdomain = filial.subdomain_name.lower() if filial.subdomain_name else None

#             data_dict = {
#                 'id': filial.id,
#                 'name': filial.name,
#                 'subdomain': subdomain,
#                 'is_main': filial.is_main,
#             }

#             structured_data['by_id'][filial.id] = data_dict
#             if subdomain:
#                 structured_data['by_subdomain'][subdomain] = data_dict

#             if filial.is_main and structured_data['main_id'] is None:
#                 structured_data['main_id'] = filial.id

#             if first_filial_pk is None:
#                 first_filial_pk = filial.id
#                 structured_data['first_id'] = filial.id

#         if structured_data['main_id'] is None:
#             structured_data['main_id'] = structured_data['first_id']

#         # --- Modification ici : Ne met en cache que si on N'EST PAS en mode DEBUG ---
#         if not settings.DEBUG:
#             cache.set(FILIALS_CACHE_KEY, structured_data, FILIALS_CACHE_TIMEOUT)

#         return structured_data

#     except Exception as e:
#         print(f"Erreur lors de la récupération ou de la structuration des données des filiales: {e}")
#         # Ne pas mettre en cache l'échec si on est en mode DEBUG pour pouvoir retenter
#         if not settings.DEBUG:
#              # Optionnel: Mettre en cache une valeur indiquant l'échec pour éviter des requêtes répétées ?
#              cache.set(FILIALS_CACHE_KEY, {}, timeout=60) # Cache un dict vide pour 1 min
#         return None

# def get_current_filial(request):
#     """
#     Détermine l'objet Filials actuel basé sur la session, le sous-domaine,
#     ou les paramètres par défaut. Ignore le cache si settings.DEBUG est True.
#     """
#     # Appelle la fonction auxiliaire qui gère maintenant le DEBUG mode
#     filials_data = _get_structured_filials_data_from_cache_or_db()

#     if not filials_data:
#         return Filials()

#     determined_id = None
#     determined_by_session = False

#     # 1. Session
#     session_id = request.session.get('current_filial_id')
#     if session_id and session_id in filials_data['by_id']:
#         determined_id = session_id
#         determined_by_session = True
#     elif session_id:
#          request.session.pop('current_filial_id', None)

#     # 2. Sous-domaine
#     if determined_id is None:
#         host = request.get_host().lower()
#         parts = host.split('.')
#         main_domain_parts = 2
#         if len(parts) > main_domain_parts:
#             subdomain = ".".join(parts[:-main_domain_parts])
#             filial_info = filials_data['by_subdomain'].get(subdomain)
#             if filial_info:
#                 determined_id = filial_info['id']

#     # 3. Fallback Principal / Premier
#     if determined_id is None:
#         determined_id = filials_data['main_id']

#     # 4. Mise à jour de la session
#     if determined_id is not None and not determined_by_session:
#          filial_info = filials_data['by_id'].get(determined_id)
#          if filial_info and not filial_info.get('subdomain'):
#               request.session['current_filial_id'] = determined_id

#     # 5. Récupération de l'objet modèle final
#     if determined_id is not None:
#         try:
#             return Filials.objects.get(id=determined_id)
#         except Filials.DoesNotExist:
#             print(f"Incohérence: Filial ID {determined_id} trouvé mais pas dans la DB.")
#             pass

#     return Filials()




def get_current_filial(request):
    """
    Détermine l'objet Filials actuel SANS utiliser le cache.
    Effectue des requêtes DB à chaque appel pour récupérer les données.
    ATTENTION : Moins performant que la version avec cache. À utiliser
    principalement pour le débogage ou si le cache n'est pas une option.

    :param request: L'objet HttpRequest.
    :return: Objet Filials ou un objet Filials() vide si aucun n'est trouvé/configuré.
    """
    # --- Étape 1: Récupérer et structurer les données depuis la DB (à chaque appel) ---
    structured_data = {
        'by_id': {},
        'by_subdomain': {},
        'main_id': None,
        'first_id': None,
    }
    try:
        # Requête pour obtenir les données nécessaires
        filials_queryset = Filials.objects.filter(isHidden=False).only(
            'id', 'name', 'subdomain_name', 'is_main'
        ).order_by('pk')

        first_filial_pk = None
        # Construction de la structure pour recherche rapide
        for filial in filials_queryset:
            filial_id = filial.id # Utilise directement l'ID numérique
            subdomain = filial.subdomain_name.lower() if filial.subdomain_name else None

            data_dict = {
                'id': filial_id,
                'name': filial.name,
                'subdomain': subdomain,
                'is_main': filial.is_main,
            }

            structured_data['by_id'][filial_id] = data_dict
            if subdomain:
                structured_data['by_subdomain'][subdomain] = data_dict

            if filial.is_main and structured_data['main_id'] is None:
                structured_data['main_id'] = filial_id

            if first_filial_pk is None:
                first_filial_pk = filial_id
                structured_data['first_id'] = filial_id

        if structured_data['main_id'] is None:
            structured_data['main_id'] = structured_data['first_id']

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des filiales (sans cache): {e}", exc_info=True)
        return Filials() # Retourne un objet vide en cas d'erreur DB

    # --- Étape 2: Logique de Détermination du Filial Actuel ---
    if not structured_data['first_id']: # Vérifie s'il y a au moins une filiale
        return Filials()

    determined_id = None
    determined_by_session = False

    # 1. Session
    session_id = request.session.get('current_filial_id')
    if session_id and session_id in structured_data['by_id']:
        determined_id = session_id
        determined_by_session = True
        logger.debug(f"Filial déterminé par session: ID {determined_id}")
    elif session_id: # Session ID existe mais n'est plus valide
         logger.debug(f"ID Filial invalide en session ({session_id}), suppression.")
         request.session.pop('current_filial_id', None)

    # 2. Sous-domaine
    if determined_id is None:
        host = request.get_host().lower()
        parts = host.split('.')
        # Ajustez main_domain_parts selon votre structure de domaine réelle
        # ex: example.com -> 1, example.co.uk -> 2, sub.example.com -> 1
        main_domain_parts = settings.MAIN_DOMAIN_PARTS if hasattr(settings, 'MAIN_DOMAIN_PARTS') else 1
        if len(parts) > main_domain_parts:
            subdomain = ".".join(parts[:-main_domain_parts])
            filial_info = structured_data['by_subdomain'].get(subdomain)
            if filial_info:
                determined_id = filial_info['id']
                logger.debug(f"Filial déterminé par sous-domaine '{subdomain}': ID {determined_id}")

    # 3. Fallback Principal / Premier
    if determined_id is None:
        determined_id = structured_data['main_id']
        if determined_id:
            logger.debug(f"Filial déterminé par défaut (principal/premier): ID {determined_id}")

    # --- Étape 3: Mise à jour de la Session ---
    if determined_id is not None and not determined_by_session:
         filial_info = structured_data['by_id'].get(determined_id)
         # Met à jour la session si le filial trouvé n'est PAS associé à un sous-domaine spécifique
         if filial_info and not filial_info.get('subdomain'):
              logger.debug(f"Mise à jour de la session avec Filial ID {determined_id} (pas de sous-domaine)")
              request.session['current_filial_id'] = determined_id
         elif filial_info:
              logger.debug(f"Ne met pas à jour la session pour le filial ID {determined_id} (associé au sous-domaine '{filial_info.get('subdomain')}')")


    # --- Étape 4: Récupération de l'Objet Modèle Final ---
    if determined_id is not None:
        try:
            # Cette requête est effectuée à chaque appel en plus de la première
            # Only() pourrait être utilisé ici si on sait quels champs sont TOUJOURS nécessaires
            current_filial = Filials.objects.get(id=determined_id)
            logger.debug(f"Retour de l'objet Filial complet: {current_filial.name}")
            return current_filial
        except Filials.DoesNotExist:
            logger.error(f"Incohérence (sans cache): Filial ID {determined_id} structuré mais introuvable en DB.", exc_info=True)
            # Si l'ID déterminé n'existe plus (cas rare), on retourne l'objet vide
            pass
        except Exception as e:
             logger.error(f"Erreur lors de la récupération finale du filial ID {determined_id}: {e}", exc_info=True)
             return Filials() # Retourne un objet vide en cas d'erreur


    logger.debug("Aucun filial déterminé, retour d'un objet Filial vide.")
    return Filials() # Retourne un objet vide si rien n'a été trouvé



# class RobotsView(TemplateView):
# 	template_name = "filials/robots.html"
	
# 	def get(self, request):
# 		filials = Filials.objects.filter(isHidden=False).only('id', 'name', 'subdomain_name', 'is_main', 'comment')
# 		robots_main = filials.filter(is_main=True).first()
# 		robots = get_current_filial(request)
# 		if robots.sitemap_name:
# 			sitemaps = robots.sitemap_name
# 		else:
# 			if robots.robots:
# 				sitemaps = 'sitemap'
# 			else:
# 				sitemaps = 'sitemap_' + robots.subdomain_name.replace(".", "").replace("/", "")
# 		robots_txt = robots_main.robots.replace('{host}', request.get_host()).replace('{sitemap}', sitemaps)
# 		if "test." in request.get_host():
# 			robots_txt = ""
# 		return render(request, self.template_name, locals(), content_type="text/plain")