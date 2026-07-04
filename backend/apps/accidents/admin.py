from django.contrib import admin

from .models import Accident, AccidentSummary


@admin.register(Accident)
class AccidentAdmin(admin.ModelAdmin):
    list_display = ("source_event_id", "year", "month", "state_region", "district_region", "category")
    search_fields = ("source_event_id",)
    list_filter = ("year", "category", "is_pedestrian", "is_bicycle", "is_car")


@admin.register(AccidentSummary)
class AccidentSummaryAdmin(admin.ModelAdmin):
    list_display = ("year", "region", "region_level", "category", "participant", "accident_count")
    list_filter = ("year", "region_level", "category", "participant")
