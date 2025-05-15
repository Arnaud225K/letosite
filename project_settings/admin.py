from django.contrib import admin
from django.contrib.admin.models import LogEntry
from rangefilter.filters import DateRangeFilterBuilder

from .models import ProjectSettings, SocialLink


class SocialLinkInline(admin.TabularInline):
  model = SocialLink
  fields = ('name', 'icon_name', 'icon_image', 'display_svg_icon', 'order_number', 'is_hidden',)
  readonly_fields = ('display_svg_icon',)
  extra = 1
  ordering = ('order_number', 'name')
  verbose_name = "Социальная ссылка"
  verbose_name_plural = "Социальные ссылки"
	
class ProjectSettingsAdmin(admin.ModelAdmin):
	list_display = ('name', 'site_name',)
	inlines = [
		SocialLinkInline,
	]
admin.site.register(ProjectSettings, ProjectSettingsAdmin)


#Custom Journal on site for LogEntry
class LogEntryAdmin(admin.ModelAdmin):
  list_display = ('action_flag', 'user', 'content_type', 'object_repr', 'get_change_message', 'action_time')
  search_fields = ('user__username', 'content_type__model','object_repr',)
  list_filter = ('action_flag', ('action_time', DateRangeFilterBuilder()),)
admin.site.register(LogEntry, LogEntryAdmin)
