from django.contrib import admin

from .models import Indicator, IndicatorValue


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "unit", "source_system")
    search_fields = ("code", "name", "source_system")


@admin.register(IndicatorValue)
class IndicatorValueAdmin(admin.ModelAdmin):
    list_display = ("indicator", "region", "year", "value", "source")
    list_filter = ("indicator", "year", "source")
