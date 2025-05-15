from django.contrib import admin

from static_text.models import StaticText


class StaticTextAdmin(admin.ModelAdmin):
	search_fields = ('slug', 'comment')
	list_display = ('slug', 'comment')
admin.site.register(StaticText, StaticTextAdmin)
