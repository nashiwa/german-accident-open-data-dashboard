import pytest
from django.core.management import call_command

from apps.accidents.models import Accident
from apps.catalog.models import ImportRun, Source


@pytest.mark.django_db
def test_import_command_loads_fallback_file(tmp_path):
    fallback = tmp_path / "accidents.csv"
    fallback.write_text(
        "OID_;UIDENTSTLAE;ULAND;UKREIS;UGEMEINDE;UJAHR;UMONAT;USTUNDE;UWOCHENTAG;UKATEGORIE;UART;UTYP1;ULICHTVERH;IstStrassenzustand;IstRad;IstPKW;IstFuss;IstKrad;IstGkfz;IstSonstige;XGCSWGS84;YGCSWGS84\n"
        "1;event-1;11;00;000;2023;05;14;2;3;5;2;0;0;0;1;0;0;0;0;13,40500000;52,52000000\n",
        encoding="utf-8-sig",
    )

    call_command(
        "import_accident_platform",
        official_accidents_2023_url="https://example.invalid/not-found.csv",
        accidents_2023_fallback=str(fallback),
        cache_dir=str(tmp_path / "cache"),
    )

    assert Accident.objects.filter(source_event_id="event-1").exists()
    run = ImportRun.objects.get()
    assert run.status == ImportRun.Status.SUCCESS
    assert run.rows_read == 1
    assert run.rows_inserted == 1
    assert run.warnings[0].startswith("official source failed:")


@pytest.mark.django_db
def test_import_command_loads_multiple_years(tmp_path, monkeypatch):
    file_2022 = tmp_path / "accidents_2022.csv"
    file_2023 = tmp_path / "accidents_2023.csv"
    header = "OID_;UIDENTSTLAE;ULAND;UKREIS;UGEMEINDE;UJAHR;UMONAT;USTUNDE;UWOCHENTAG;UKATEGORIE;UART;UTYP1;ULICHTVERH;IstStrassenzustand;IstRad;IstPKW;IstFuss;IstKrad;IstGkfz;IstSonstige;XGCSWGS84;YGCSWGS84\n"
    file_2022.write_text(
        header + "1;event-2022;01;001;0001;2022;05;14;2;3;5;2;0;0;0;1;0;0;0;0;13,40500000;52,52000000\n",
        encoding="utf-8-sig",
    )
    file_2023.write_text(
        header + "1;event-2023;01;001;0001;2023;06;15;3;3;5;2;0;0;1;0;0;0;0;0;13,40500000;52,52000000\n",
        encoding="utf-8-sig",
    )
    fallback_by_year = {2022: str(file_2022), 2023: str(file_2023)}

    monkeypatch.setattr(
        "apps.importer.management.commands.import_accident_platform._fallback_path_for_year",
        lambda project_root, configured_fallback, year: fallback_by_year[year],
    )

    call_command(
        "import_accident_platform",
        official_accidents_2023_url="https://example.invalid/not-found-2023.csv",
        cache_dir=str(tmp_path / "cache"),
        years=[2022, 2023],
    )

    assert set(Accident.objects.values_list("year", flat=True)) == {2022, 2023}
    assert ImportRun.objects.count() == 2
    assert Source.objects.filter(name="OPAL Unfallatlas 2022 fallback").exists()
    assert Source.objects.filter(name="OPAL Unfallatlas 2023 fallback").exists()
