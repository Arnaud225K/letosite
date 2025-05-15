from django.shortcuts import render

from django.template import Context, Template

from letosite.views import global_views
from .models import StaticText
from filials.views import get_current_filial


def get_static_text(request, global_context, slug):
	try:
		global_context.update(global_views(request))
		try:
			current_filial = get_current_filial(request)
			region = slug
			if current_filial.subdomain_name == '/':
				region += '_main'
			else:
				region += '_'
				region += current_filial.subdomain_name[:-1]
			html_static_text = Template(StaticText.objects.get(slug=region).text).render(Context(global_context))
		except:
			html_static_text = Template(StaticText.objects.get(slug=slug).text).render(Context(global_context))
	except:
		html_static_text = ''
	return html_static_text


def static_text(request):
	static_text_list = {}
	for item in list(StaticText.objects.values('slug', 'text').distinct().order_by('slug')):
		static_text_list[item['slug']] = item
	
	try:
		text_cover_home_page_1 = static_text_list['text_cover_home_page_1']['text']
	except:
		text_cover_home_page_1 = ""

	# try:
	# 	text_cover_home_page_2 = static_text_list['text_cover_home_page_2']['text']
	# except:
	# 	text_cover_home_page_2 = ""

	# try:
	# 	text_material_karkas_product_page = static_text_list['text_material_karkas_product_page']['text']
	# except:
	# 	text_material_karkas_product_page = ""

	# try:
	# 	text_material_kirpich_product_page = static_text_list['text_material_kirpich_product_page']['text']
	# except:
	# 	text_material_kirpich_product_page = ""

	# try:
	# 	text_material_gazoblok_product_page = static_text_list['text_material_gazoblok_product_page']['text']
	# except:
	# 	text_material_gazoblok_product_page = ""

	# try:
	# 	text_material_brus_product_page = static_text_list['text_material_brus_product_page']['text']
	# except:
	# 	text_material_brus_product_page = ""

	# try:
	# 	text_material_penoblok_product_page = static_text_list['text_material_penoblok_product_page']['text']
	# except:
	# 	text_material_penoblok_product_page = ""
		
	return locals()

