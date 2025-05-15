from django.contrib import admin

from .models import SearchTerm, SearchChange, SearchRemove


class SearchTermAdmin(admin.ModelAdmin):
	list_display = ('q', 'search_date', 'ip_address')
	search_fields = ('ip_address', 'q')


admin.site.register(SearchTerm, SearchTermAdmin)


class SearchChangeAdmin(admin.ModelAdmin):
	search_fields = ('source', 'result')
	list_display = ('source', 'result')


admin.site.register(SearchChange, SearchChangeAdmin)
admin.site.register(SearchRemove)
