from django.contrib import admin

from .models import Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("ags", "name", "level", "state_code", "parent", "population")
    search_fields = ("ags", "name", "state_name")
    list_filter = ("level", "state_code")
