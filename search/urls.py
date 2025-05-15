from django.urls import path
from .views import SearchView

app_name = 'search'
urlpatterns = [
    path('results/', SearchView.as_view(), name='results'),
]
