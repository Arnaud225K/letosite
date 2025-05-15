from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
# from filials.views import RobotsView
from . import settings
import debug_toolbar
from django.conf.urls.static import static
from .settings import SITE_NAME
from .views import page404, page500
from .views import page404, page500


#Custom admin site
admin.site.site_header = SITE_NAME
admin.site.site_title = SITE_NAME


handler404 = page404
handler500 = page500


urlpatterns = [
    path('panadmin/', admin.site.urls),
]

#Activate debug toolbar url
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]

urlpatterns += [
    #Custom App url
    # path('promo/', include('promo.urls')),
    path('search/', include('search.urls')),
    path('select2/', include('django_select2.urls')),
    path('admin_m/', include('admin_m.urls')),
    path('checkout/', include('checkout.urls')),
    path('',include('menu.urls')),
    #Custom library url
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]

#Serve static files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)	
urlpatterns += [
        re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.WWW_ROOT}),
    ]