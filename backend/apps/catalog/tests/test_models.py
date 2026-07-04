import pytest

from apps.catalog.models import ImportRun, Source


@pytest.mark.django_db
def test_source_string_uses_name_and_provider():
    source = Source.objects.create(
        name="Unfallatlas 2023",
        source_type=Source.SourceType.OFFICIAL_DOWNLOAD,
        url_or_path="https://example.test/unfallatlas.csv",
        provider="Statistische Aemter",
        licence="dl-de/by-2-0",
    )

    assert str(source) == "Unfallatlas 2023 (Statistische Aemter)"


@pytest.mark.django_db
def test_import_run_tracks_row_counts():
    source = Source.objects.create(
        name="OPAL fallback",
        source_type=Source.SourceType.OPAL_FALLBACK,
        url_or_path="/data/accident_per_location_2023.csv",
        provider="TU Chemnitz OPAL",
        licence="course fallback data",
    )
    run = ImportRun.objects.create(
        source=source,
        status=ImportRun.Status.SUCCESS,
        checksum="abc123",
        rows_read=10,
        rows_inserted=8,
        rows_updated=2,
    )

    assert run.rows_read == 10
    assert run.status == ImportRun.Status.SUCCESS
