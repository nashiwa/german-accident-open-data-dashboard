from django.db import models


class Indicator(models.Model):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=64)
    source_system = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.unit})"


class IndicatorValue(models.Model):
    region = models.ForeignKey("regions.Region", on_delete=models.CASCADE, related_name="indicator_values")
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name="values")
    year = models.PositiveIntegerField()
    value = models.DecimalField(max_digits=18, decimal_places=4)
    source = models.ForeignKey("catalog.Source", on_delete=models.PROTECT)
    import_run = models.ForeignKey("catalog.ImportRun", on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["region", "indicator", "year"], name="unique_indicator_value"),
        ]
        indexes = [
            models.Index(fields=["region", "year"]),
            models.Index(fields=["indicator", "year"]),
        ]

    def __str__(self):
        return f"{self.indicator.code} {self.region} {self.year}"
