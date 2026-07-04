from django.db import models


class Accident(models.Model):
    source_event_id = models.CharField(max_length=128)
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    hour = models.PositiveIntegerField(null=True, blank=True)
    weekday = models.PositiveIntegerField(null=True, blank=True)
    category = models.CharField(max_length=32, blank=True)
    accident_type = models.CharField(max_length=32, blank=True)
    light_condition = models.CharField(max_length=32, blank=True)
    road_condition = models.CharField(max_length=32, blank=True)
    is_bicycle = models.BooleanField(default=False)
    is_car = models.BooleanField(default=False)
    is_pedestrian = models.BooleanField(default=False)
    is_motorcycle = models.BooleanField(default=False)
    is_goods_vehicle = models.BooleanField(default=False)
    is_other = models.BooleanField(default=False)
    longitude = models.DecimalField(max_digits=12, decimal_places=8)
    latitude = models.DecimalField(max_digits=12, decimal_places=8)
    state_region = models.ForeignKey("regions.Region", null=True, blank=True, on_delete=models.PROTECT, related_name="state_accidents")
    district_region = models.ForeignKey("regions.Region", null=True, blank=True, on_delete=models.PROTECT, related_name="district_accidents")
    municipality_region = models.ForeignKey("regions.Region", null=True, blank=True, on_delete=models.PROTECT, related_name="municipality_accidents")
    source = models.ForeignKey("catalog.Source", on_delete=models.PROTECT)
    import_run = models.ForeignKey("catalog.ImportRun", on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["source", "source_event_id"], name="unique_accident_per_source_event"),
        ]
        indexes = [
            models.Index(fields=["year"]),
            models.Index(fields=["year", "state_region"]),
            models.Index(fields=["year", "district_region"]),
            models.Index(fields=["category"]),
            models.Index(fields=["is_pedestrian"]),
            models.Index(fields=["is_bicycle"]),
        ]

    def __str__(self):
        return f"{self.source_event_id} ({self.year})"


class AccidentSummary(models.Model):
    year = models.PositiveIntegerField()
    region = models.ForeignKey("regions.Region", on_delete=models.CASCADE)
    region_level = models.CharField(max_length=32)
    category = models.CharField(max_length=32, blank=True)
    participant = models.CharField(max_length=32, blank=True)
    accident_count = models.PositiveIntegerField()
    source_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["year", "region", "category", "participant"], name="unique_accident_summary"),
        ]
        indexes = [
            models.Index(fields=["year", "region_level"]),
            models.Index(fields=["year", "region"]),
        ]

    def __str__(self):
        return f"{self.region} {self.year}: {self.accident_count}"
