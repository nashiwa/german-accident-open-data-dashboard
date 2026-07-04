from django.db import models


class Region(models.Model):
    class Level(models.TextChoices):
        STATE = "state", "State"
        DISTRICT = "district", "District"
        MUNICIPALITY = "municipality", "Municipality"

    ags = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=32, choices=Level.choices)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="children")
    state_code = models.CharField(max_length=8, blank=True)
    state_name = models.CharField(max_length=255, blank=True)
    population = models.PositiveIntegerField(null=True, blank=True)
    area_km2 = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    geometry_source_id = models.CharField(max_length=255, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["ags"]),
            models.Index(fields=["level"]),
            models.Index(fields=["state_code", "level"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.level})"
