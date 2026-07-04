import pytest

from apps.accidents.models import Accident
from apps.catalog.models import ImportRun, Source
from apps.importer.services.loaders import load_accidents


@pytest.mark.django_db
def test_load_accidents_is_idempotent():
    source = Source.objects.create(
        name="OPAL Unfallatlas 2023",
        source_type=Source.SourceType.OPAL_FALLBACK,
        url_or_path="/data/accident_per_location_2023.csv",
        provider="TU Chemnitz OPAL",
        licence="course fallback data",
    )
    run = ImportRun.objects.create(source=source)
    rows = [{
        "source_event_id": "event-1",
        "source_state": "11",
        "source_regbez": "0",
        "source_district": "00",
        "source_municipality": "000",
        "year": 2023,
        "month": 5,
        "hour": 14,
        "weekday": 2,
        "category": "3",
        "accident_type": "5",
        "light_condition": "0",
        "road_condition": "0",
        "is_bicycle": False,
        "is_car": True,
        "is_pedestrian": False,
        "is_motorcycle": False,
        "is_goods_vehicle": False,
        "is_other": False,
        "longitude": "13.40500000",
        "latitude": "52.52000000",
    }]

    first = load_accidents(rows, source, run)
    second = load_accidents(rows, source, run)

    assert first.inserted == 1
    assert second.updated == 1
    assert Accident.objects.count() == 1


@pytest.mark.django_db
def test_load_accidents_ignores_parser_only_source_region_fields():
    source = Source.objects.create(
        name="OPAL Unfallatlas 2023",
        source_type=Source.SourceType.OPAL_FALLBACK,
        url_or_path="/data/accident_per_location_2023.csv",
        provider="TU Chemnitz OPAL",
        licence="course fallback data",
    )
    run = ImportRun.objects.create(source=source)
    load_accidents([{
        "source_event_id": "event-2",
        "source_state": "14",
        "source_regbez": "6",
        "source_district": "12",
        "source_municipality": "000",
        "year": 2023,
        "month": 5,
        "longitude": "10.14887539",
        "latitude": "54.30695105",
    }], source, run)

    accident = Accident.objects.get(source_event_id="event-2")
    assert accident.year == 2023
    assert accident.state_region.state_code == "SN"
    assert accident.district_region.ags == "14612"
