import pytest
from django.urls import reverse

from apps.accidents.models import Accident
from apps.catalog.models import ImportRun, Source
from apps.regions.models import Region


@pytest.fixture
def question_seed_data():
    source = Source.objects.create(
        name="Question source",
        source_type=Source.SourceType.OPAL_FALLBACK,
        url_or_path="/data/questions.csv",
        provider="test",
        licence="test",
    )
    run = ImportRun.objects.create(source=source, status=ImportRun.Status.SUCCESS)
    berlin = Region.objects.create(ags="11", name="Berlin", level=Region.Level.STATE, state_code="BE")
    saxony = Region.objects.create(ags="14", name="Sachsen", level=Region.Level.STATE, state_code="SN")
    Accident.objects.create(source=source, import_run=run, source_event_id="old", year=2021, month=1, longitude=13, latitude=52, state_region=saxony)
    Accident.objects.create(source=source, import_run=run, source_event_id="sn", year=2023, month=1, longitude=13, latitude=52, state_region=saxony)
    Accident.objects.create(source=source, import_run=run, source_event_id="be", year=2023, month=1, longitude=13, latitude=52, state_region=berlin, is_pedestrian=True)


@pytest.mark.django_db
def test_mandatory_questions_endpoint_shape(client, question_seed_data):
    response = client.get(reverse("api-mandatory-questions"))

    assert response.status_code == 200
    payload = response.json()
    assert set(payload["questions"]) == {
        "earliest_accident_year",
        "saxony_accidents_2023",
        "nrw_earliest_year",
        "mecklenburg_vorpommern_earliest_year",
        "berlin_pedestrian_accidents_2023",
        "top_districts_by_accident_rate",
    }
    assert payload["questions"]["earliest_accident_year"]["answer"]["earliest_year"] == 2021
    assert payload["questions"]["saxony_accidents_2023"]["answer"]["accident_count"] == 1
    assert payload["questions"]["berlin_pedestrian_accidents_2023"]["answer"]["accident_count"] == 1
    assert payload["provenance"][0]["source"] == "Question source"


@pytest.mark.django_db
def test_named_question_endpoint_returns_question_answer_and_provenance(client, question_seed_data):
    response = client.get(reverse("api-question-berlin-pedestrian-accidents-2023"))

    assert response.status_code == 200
    payload = response.json()
    assert "question" in payload
    assert payload["answer"]["accident_count"] == 1
    assert payload["provenance"][0]["source"] == "Question source"
