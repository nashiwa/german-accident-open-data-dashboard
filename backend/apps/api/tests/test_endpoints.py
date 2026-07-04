import pytest
from django.urls import reverse

from apps.accidents.models import Accident
from apps.catalog.models import ImportRun, Source
from apps.regions.models import Region


@pytest.fixture
def api_seed_data():
    source = Source.objects.create(
        name="OPAL Unfallatlas 2023 fallback",
        source_type=Source.SourceType.OPAL_FALLBACK,
        url_or_path="/data/accident_per_location_2023.csv",
        provider="TU Chemnitz OPAL",
        licence="course fallback data",
    )
    run = ImportRun.objects.create(source=source, status=ImportRun.Status.SUCCESS, rows_read=2, rows_inserted=2)
    state = Region.objects.create(ags="14", name="Sachsen", level=Region.Level.STATE, state_code="SN", state_name="Sachsen")
    Accident.objects.create(
        source=source,
        import_run=run,
        source_event_id="sn-1",
        year=2023,
        month=5,
        longitude=13.7,
        latitude=51.0,
        state_region=state,
        is_bicycle=True,
    )
    return {"source": source, "run": run, "state": state}


@pytest.mark.django_db
def test_regions_endpoint_filters_by_level(client, api_seed_data):
    response = client.get(reverse("api-regions"), {"level": "state"})

    assert response.status_code == 200
    assert response.json()[0]["ags"] == "14"


@pytest.mark.django_db
def test_region_detail_returns_404_for_unknown_ags(client):
    response = client.get(reverse("api-region-detail", kwargs={"ags": "99999"}))

    assert response.status_code == 404


@pytest.mark.django_db
def test_accidents_endpoint_returns_preview(client, api_seed_data):
    response = client.get(reverse("api-accidents"), {"year": 2023, "state": "SN"})

    assert response.status_code == 200
    assert response.json()[0]["source_event_id"] == "sn-1"


@pytest.mark.django_db
def test_aggregate_accidents_returns_count_and_provenance(client, api_seed_data):
    response = client.get(reverse("api-aggregate-accidents"), {"year": 2023, "state": "SN", "participant": "bicycle"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["accident_count"] == 1
    assert payload["provenance"][0]["source"] == "OPAL Unfallatlas 2023 fallback"


@pytest.mark.django_db
def test_aggregate_accidents_rejects_bad_year(client):
    response = client.get(reverse("api-aggregate-accidents"), {"year": "not-a-year"})

    assert response.status_code == 400
    assert response.json()["detail"] == "year must be an integer"
