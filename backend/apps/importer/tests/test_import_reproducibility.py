import pytest
from django.core.management import call_command

from apps.accidents.models import Accident
from apps.catalog.models import ImportRun


@pytest.mark.django_db
def test_import_command_is_reproducible_for_same_source_file(tmp_path):
    fallback = tmp_path / "accidents.csv"
    fallback.write_text(
        "OID_;UIDENTSTLAE;ULAND;UKREIS;UGEMEINDE;UJAHR;UMONAT;USTUNDE;UWOCHENTAG;UKATEGORIE;UART;UTYP1;ULICHTVERH;IstStrassenzustand;IstRad;IstPKW;IstFuss;IstKrad;IstGkfz;IstSonstige;XGCSWGS84;YGCSWGS84\n"
        "1;event-1;01;001;0001;2023;05;14;2;3;5;2;0;0;0;1;0;0;0;0;13,40500000;52,52000000\n",
        encoding="utf-8-sig",
    )
    command_options = {
        "official_accidents_2023_url": "https://example.invalid/not-found.csv",
        "accidents_2023_fallback": str(fallback),
        "cache_dir": str(tmp_path / "cache"),
    }

    call_command("import_accident_platform", **command_options)
    call_command("import_accident_platform", **command_options)

    assert Accident.objects.filter(source_event_id="event-1").count() == 1
    assert ImportRun.objects.count() == 2

    first_run, second_run = ImportRun.objects.order_by("started_at")
    assert first_run.rows_inserted == 1
    assert first_run.rows_updated == 0
    assert second_run.rows_inserted == 0
    assert second_run.rows_updated == 1
