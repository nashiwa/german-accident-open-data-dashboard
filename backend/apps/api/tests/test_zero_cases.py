import pytest
from django.urls import reverse

from apps.accidents.models import Accident
from apps.api.services.queries import zero_accident_municipalities
from apps.catalog.models import ImportRun, Source
from apps.regions.models import Region


@pytest.fixture
def zero_case_seed_data():
    source = Source.objects.create(
        name="Zero case source",
        source_type=Source.SourceType.OPAL_FALLBACK,
        url_or_path="/data/zero.csv",
        provider="test",
        licence="test",
    )
    run = ImportRun.objects.create(source=source, status=ImportRun.Status.SUCCESS)
    state = Region.objects.create(ags="01", name="Schleswig-Holstein", level=Region.Level.STATE, state_code="SH")
    district = Region.objects.create(ags="01001", name="District", level=Region.Level.DISTRICT, parent=state, state_code="SH")
    no_accident = Region.objects.create(ags="010010001", name="No Accident", level=Region.Level.MUNICIPALITY, parent=district, state_code="SH")
    with_accident = Region.objects.create(ags="010010002", name="With Accident", level=Region.Level.MUNICIPALITY, parent=district, state_code="SH")
    other_year = Region.objects.create(ags="010010003", name="Other Year", level=Region.Level.MUNICIPALITY, parent=district, state_code="SH")

    Accident.objects.create(
        source=source,
        import_run=run,
        source_event_id="event-current",
        year=2023,
        month=1,
        longitude=10,
        latitude=54,
        state_region=state,
        district_region=district,
        municipality_region=with_accident,
    )
    Accident.objects.create(
        source=source,
        import_run=run,
        source_event_id="event-old",
        year=2022,
        month=1,
        longitude=10,
        latitude=54,
        state_region=state,
        district_region=district,
        municipality_region=other_year,
    )
    return no_accident, other_year, with_accident


@pytest.mark.django_db
def test_zero_accident_municipalities_returns_regions_without_events_in_year(zero_case_seed_data):
    no_accident, other_year, with_accident = zero_case_seed_data

    result = list(zero_accident_municipalities(year=2023, state_code="SH"))

    assert [region.ags for region in result] == [no_accident.ags, other_year.ags]
    assert with_accident not in result


@pytest.mark.django_db
def test_zero_accident_municipalities_endpoint_returns_serialized_regions(client, zero_case_seed_data):
    response = client.get(reverse("api-bonus-zero-accident-municipalities"), {"year": 2023, "state": "SH"})

    assert response.status_code == 200
    assert [region["ags"] for region in response.json()] == ["010010001", "010010003"]


@pytest.mark.django_db
def test_zero_accident_municipalities_endpoint_requires_year_and_state(client):
    response = client.get(reverse("api-bonus-zero-accident-municipalities"))

    assert response.status_code == 400
    assert response.json()["detail"] == "year is required"


@pytest.mark.django_db
def test_bonus_accident_points_endpoint_returns_lightweight_coordinates(client, zero_case_seed_data):
    response = client.get(reverse("api-bonus-accident-points"), {"year": 2023, "state": "SH"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["filters"] == {"year": 2023, "state": "SH", "participant": None}
    assert payload["results"] == [
        {
            "id": "event-current",
            "longitude": 10.0,
            "latitude": 54.0,
            "participant": "other",
        }
    ]
