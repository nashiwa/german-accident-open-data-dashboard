from django.db import models


class Source(models.Model):
    class SourceType(models.TextChoices):
        OFFICIAL_DOWNLOAD = "official_download", "Official download"
        OPAL_FALLBACK = "opal_fallback", "OPAL fallback"
        MANUAL_REFERENCE = "manual_reference", "Manual reference"

    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=32, choices=SourceType.choices)
    url_or_path = models.TextField()
    provider = models.CharField(max_length=255)
    licence = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["source_type"]),
            models.Index(fields=["provider"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.provider})"


class ImportRun(models.Model):
    class Status(models.TextChoices):
        STARTED = "started", "Started"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name="import_runs")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.STARTED)
    checksum = models.CharField(max_length=128, blank=True)
    rows_read = models.PositiveIntegerField(default=0)
    rows_inserted = models.PositiveIntegerField(default=0)
    rows_updated = models.PositiveIntegerField(default=0)
    warnings = models.JSONField(default=list, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["source", "status"]),
            models.Index(fields=["started_at"]),
        ]

    def __str__(self):
        return f"{self.source.name} import {self.status}"
