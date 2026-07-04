import pytest

from apps.accidents.models import Accident
from apps.api.services.queries import accident_count, accident_counts_by_region, earliest_accident_year, earliest_year_for_state
from apps.catalog.models import ImportRun, Source
from apps.regions.models import Region


@pytest.fixture
def source_and_run():
    source = Source.objects.create(
        name="Test",
        source_type=Source.SourceType.OPAL_FALLBACK,
        url_or_path="/tmp/test.csv",
        provider="test",
        licence="test",
    )
    run = ImportRun.objects.create(source=source, status=ImportRun.Status.SUCCESS)
    return source, run


@pytest.mark.django_db
def test_earliest_accident_year_returns_minimum(source_and_run):
    source, run = source_and_run
    Accident.objects.create(source=source, import_run=run, source_event_id="2", year=2023, month=1, longitude=13, latitude=52)
    Accident.objects.create(source=source, import_run=run, source_event_id="1", year=2021, month=1, longitude=13, latitude=52)

    assert earliest_accident_year() == 2021


@pytest.mark.django_db
def test_accident_count_filters_by_state_and_participant(source_and_run):
    source, run = source_and_run
    berlin = Region.objects.create(ags="11", name="Berlin", level=Region.Level.STATE, state_code="BE")
    saxony = Region.objects.create(ags="14", name="Sachsen", level=Region.Level.STATE, state_code="SN")
    Accident.objects.create(source=source, import_run=run, source_event_id="be-1", year=2023, month=1, longitude=13, latitude=52, state_region=berlin, is_pedestrian=True)
    Accident.objects.create(source=source, import_run=run, source_event_id="sn-1", year=2023, month=1, longitude=13, latitude=52, state_region=saxony, is_pedestrian=True)

    assert accident_count(year=2023, state_code="BE", participant="pedestrian") == 1
    assert earliest_year_for_state("SN") == 2023


@pytest.mark.django_db
def test_accident_counts_by_region_groups_counts(source_and_run):
    source, run = source_and_run
    saxony = Region.objects.create(ags="14", name="Sachsen", level=Region.Level.STATE, state_code="SN")
    Accident.objects.create(source=source, import_run=run, source_event_id="sn-1", year=2023, month=1, longitude=13, latitude=52, state_region=saxony)
    Accident.objects.create(source=source, import_run=run, source_event_id="sn-2", year=2023, month=1, longitude=13, latitude=52, state_region=saxony)

    result = list(accident_counts_by_region(level=Region.Level.STATE, year=2023))

    assert result[0]["state_region__ags"] == "14"
    assert result[0]["accident_count"] == 2
