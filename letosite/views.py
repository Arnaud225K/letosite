import datetime
import json
import os
from . import settings
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.shortcuts import render

from django.core.cache import cache

from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from project_settings.models import ProjectSettings, SocialLink

from filials.models import Filials
from filials.views import get_current_filial

from menu.models import MenuCatalog
# from robots.models import RobotsTxt
from checkout.cart import CartManager

MAX_ITEM_IN_FILE = 20000



def get_project_settings_cached():
    """
    Helper function to retrieve project settings from cache or DB.
    (This is the function from the previous answer)
    """
    cache_key = 'project_settings_main'
    cached_settings = cache.get(cache_key)

    if cached_settings is None:
        # print(f"CACHE MISS: Fetching settings for key '{cache_key}' from database.")
        try:
            settings_obj = ProjectSettings.objects.only(
                'id', 'name', 'start_year', 'site_name'
            ).first()

            if settings_obj:
                cached_settings = {
                    'id': settings_obj.id,
                    'name': settings_obj.name,
                    'start_year': settings_obj.start_year,
                    'site_name': settings_obj.site_name,
                }
                # Cache for 1 hour
                cache.set(cache_key, cached_settings, timeout=60*60)
            else:
                print("Project settings object not found in database.")
                cached_settings = {}
                cache.set(cache_key, cached_settings, timeout=60*5) # Cache 'missing' state

        except Exception as e:
            print(f"Error fetching project settings: {e}")
            return {} # Return empty dict on error

    else:
        # print(f"CACHE HIT: Using cached settings for key '{cache_key}'.") # for debugging
        pass

    return cached_settings


def global_views(request):
    """
    Context processor providing global template variables.
    Optimized with caching for project settings and social links.
    """
    # --- Project Settings (Cached) ---
    project_settings_data = get_project_settings_cached()
    start_year = project_settings_data.get('start_year')
    site_name_from_db = project_settings_data.get('site_name')

    # --- Social Links (Cached) ---
    cache_key_social = 'social_links_active'
    social_link = cache.get(cache_key_social)
    if social_link is None:
        print(f"CACHE MISS: Fetching social links for key '{cache_key_social}' from database.")
        social_link = SocialLink.objects.filter(is_hidden=False).only('id', 'icon_name', 'name', 'icon_image',).order_by('order_number')
        cache.set(cache_key_social, list(social_link), timeout=60*60)
    else:
        # print(f"CACHE HIT: Using cached social links for key '{cache_key_social}'.")
        pass

    # --- Other Context Variables ---
    current_year = datetime.date.today().year
    url_site = settings.SITE_NAME 
    current_url = request.build_absolute_uri()
    version_name = settings.VERSION_NAME
    site_header = settings.SITE_NAME
    site_title = f"{site_header} {version_name}"
    media_url = settings.MEDIA_URL
    static_url = settings.STATIC_URL
    current_filial = get_current_filial(request)


    context = {
        'current_year': current_year,
        'project_settings': project_settings_data,
        'start_year': start_year,
        'url_site': url_site,
        'current_url': current_url,
        'social_link': social_link,
        'version_name': version_name,
        'site_header': site_header,
        'site_title': site_title,
        'site_name': site_name_from_db or settings.SITE_NAME,
        'media_url': media_url,
        'static_url': static_url,
        'current_filial': current_filial,
    }
    return context


def cart_context(request):
    cart = CartManager(request)
    cart_data = cart.get_cart_data()
    # # --- Log pour débogage ---
    # print(f"Context Processor - Cart Data: {cart_data}")
    # print(f"Context Processor - Items Count: {len(cart_data)}")
    # # ------------------------
    cart_items_count = len(cart_data)
    return {'cart_total_items': cart_items_count}


#Page Error 404
def page404(request, exception):
	is_generic_error_404 = True
	response = render(request, 'catalog/404.html', {'is_generic_error_404': is_generic_error_404})
	response.status_code = 404
	return response


#Page Error 500
def page500(request):
	is_generic_error_500 = True
	response = render(request, 'catalog/500.html', {'is_generic_error_500': is_generic_error_500} )
	response.status_code = 500
	return response