from django.contrib import admin

from filials.models import Filials


class FilialsAdmin(admin.ModelAdmin):
    list_display = ('name','address', 'phone', 'email',)
    search_fields = ('name',)
admin.site.register(Filials, FilialsAdmin)