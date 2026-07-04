from django.contrib import admin

from .models import ImportRun, Source


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "source_type", "provider", "licence", "created_at")
    search_fields = ("name", "provider", "url_or_path")
    list_filter = ("source_type", "provider")


@admin.register(ImportRun)
class ImportRunAdmin(admin.ModelAdmin):
    list_display = ("source", "status", "started_at", "finished_at", "rows_read", "rows_inserted", "rows_updated")
    list_filter = ("status", "source")
