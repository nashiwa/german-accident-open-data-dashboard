from rest_framework import serializers

from apps.accidents.models import Accident
from apps.catalog.models import ImportRun, Source
from apps.regions.models import Region


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ["ags", "name", "level", "parent_id", "state_code", "state_name", "population", "area_km2"]


class AccidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accident
        fields = [
            "source_event_id",
            "year",
            "month",
            "hour",
            "weekday",
            "category",
            "accident_type",
            "light_condition",
            "road_condition",
            "is_bicycle",
            "is_car",
            "is_pedestrian",
            "is_motorcycle",
            "is_goods_vehicle",
            "is_other",
            "longitude",
            "latitude",
            "state_region_id",
            "district_region_id",
            "municipality_region_id",
        ]


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ["id", "name", "source_type", "url_or_path", "provider", "licence", "description"]


class ImportRunSerializer(serializers.ModelSerializer):
    source = SourceSerializer()

    class Meta:
        model = ImportRun
        fields = [
            "id",
            "source",
            "started_at",
            "finished_at",
            "status",
            "checksum",
            "rows_read",
            "rows_inserted",
            "rows_updated",
            "warnings",
        ]
