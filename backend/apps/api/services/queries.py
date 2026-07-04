from django.db.models import Count, Min

from apps.accidents.models import Accident
from apps.indicators.models import IndicatorValue
from apps.regions.models import Region


PARTICIPANT_FILTERS = {
    "pedestrian": "is_pedestrian",
    "bicycle": "is_bicycle",
    "car": "is_car",
    "motorcycle": "is_motorcycle",
    "goods_vehicle": "is_goods_vehicle",
    "other": "is_other",
}


def _apply_accident_filters(queryset, *, year=None, state_code=None, category=None, participant=None):
    if year is not None:
        queryset = queryset.filter(year=year)
    if state_code:
        queryset = queryset.filter(state_region__state_code=state_code)
    if category:
        queryset = queryset.filter(category=category)
    if participant:
        participant_field = PARTICIPANT_FILTERS.get(participant)
        if participant_field is None:
            raise ValueError(f"Unsupported participant filter: {participant}")
        queryset = queryset.filter(**{participant_field: True})
    return queryset


def earliest_accident_year():
    return Accident.objects.aggregate(value=Min("year"))["value"]


def accident_count(year=None, state_code=None, category=None, participant=None):
    queryset = _apply_accident_filters(
        Accident.objects.all(),
        year=year,
        state_code=state_code,
        category=category,
        participant=participant,
    )
    return queryset.count()


def earliest_year_for_state(state_code):
    return Accident.objects.filter(state_region__state_code=state_code).aggregate(value=Min("year"))["value"]


def accident_counts_by_region(level, year, category=None, participant=None):
    region_field = {
        Region.Level.STATE: "state_region",
        Region.Level.DISTRICT: "district_region",
        Region.Level.MUNICIPALITY: "municipality_region",
    }[level]
    queryset = _apply_accident_filters(Accident.objects.filter(**{f"{region_field}__isnull": False}), year=year, category=category, participant=participant)
    return (
        queryset.values(f"{region_field}__ags", f"{region_field}__name", f"{region_field}__level")
        .annotate(accident_count=Count("id"))
        .order_by("-accident_count", f"{region_field}__ags")
    )


def accident_rates_by_population(level, year, limit=10):
    counts = list(accident_counts_by_region(level=level, year=year))
    region_ags = [row[f"{level}_region__ags"] for row in counts if f"{level}_region__ags" in row]
    population_values = {
        value.region.ags: value.value
        for value in IndicatorValue.objects.select_related("region", "indicator")
        .filter(region__ags__in=region_ags, year=year, indicator__code="population")
    }
    rates = []
    for row in counts:
        ags = row.get(f"{level}_region__ags")
        population = population_values.get(ags)
        if not population:
            continue
        rates.append({
            "ags": ags,
            "name": row.get(f"{level}_region__name"),
            "level": row.get(f"{level}_region__level"),
            "year": year,
            "accident_count": row["accident_count"],
            "population": int(population),
            "rate_per_100000": round((row["accident_count"] / float(population)) * 100000, 2),
        })
    return sorted(rates, key=lambda item: item["rate_per_100000"], reverse=True)[:limit]


def zero_accident_municipalities(year, state_code):
    return (
        Region.objects.filter(level=Region.Level.MUNICIPALITY, state_code=state_code)
        .exclude(municipality_accidents__year=year)
        .order_by("ags")
    )
