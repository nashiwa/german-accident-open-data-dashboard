from dataclasses import dataclass
from decimal import Decimal

from apps.accidents.models import Accident
from apps.importer.services.region_codes import assign_regions_from_source_codes


ACCIDENT_MODEL_FIELDS = {
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
    "state_region",
    "district_region",
    "municipality_region",
}


@dataclass
class LoadResult:
    inserted: int = 0
    updated: int = 0


def _accident_defaults(row, source, import_run):
    defaults = {key: value for key, value in row.items() if key in ACCIDENT_MODEL_FIELDS}
    defaults.update(assign_regions_from_source_codes(row))
    defaults["longitude"] = Decimal(str(defaults["longitude"]))
    defaults["latitude"] = Decimal(str(defaults["latitude"]))
    defaults["source"] = source
    defaults["import_run"] = import_run
    return defaults


def load_accidents(rows, source, import_run) -> LoadResult:
    result = LoadResult()
    for row in rows:
        _, created = Accident.objects.update_or_create(
            source=source,
            source_event_id=row["source_event_id"],
            defaults=_accident_defaults(row, source, import_run),
        )
        if created:
            result.inserted += 1
        else:
            result.updated += 1
    return result
