from django.urls import path , re_path

from django.views.decorators.cache import cache_page
from . import views

app_name = 'menu'
urlpatterns = [
	path('', views.IndexView.as_view(), name='index'),
    path('ajax/filter-products/', views.FilterProductsView.as_view(), name='ajax_filter_products'),
    path('ajax/menu-dropdown-content/', views.ajax_get_menu_dropdown_content, name='ajax_menu_dropdown_content'),
    path('product/<str:product_slug>/', views.ProductView.as_view(), name='product'),
    path('<path:hierarchy>/f/<path:filter_segment>/', views.MenuView.as_view(), name='menu_catalog_filtered'),
    path('<path:hierarchy>/', views.MenuView.as_view(), name='menu_catalog'),
]