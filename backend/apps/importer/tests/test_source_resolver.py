from pathlib import Path

from apps.importer.source_resolver import SourceCandidate, resolve_source


def test_resolve_source_uses_fallback_when_download_fails(tmp_path):
    fallback = tmp_path / "accident_per_location_2023.csv"
    fallback.write_text("OID_;UJAHR\n1;2023\n", encoding="utf-8")

    def failing_download(candidate, target_dir):
        raise RuntimeError("HTTP 503")

    selected = resolve_source(
        official=SourceCandidate(name="Unfallatlas 2023", url_or_path="https://example.test/data.csv", source_type="official_download"),
        fallback=SourceCandidate(name="OPAL Unfallatlas 2023", url_or_path=str(fallback), source_type="opal_fallback"),
        cache_dir=tmp_path,
        download_func=failing_download,
    )

    assert selected.source_type == "opal_fallback"
    assert Path(selected.local_path).exists()
    assert selected.warning == "official source failed: HTTP 503"


def test_resolve_source_prefers_successful_official_download(tmp_path):
    official_file = tmp_path / "official.csv"
    official_file.write_text("OID_;UJAHR\n1;2023\n", encoding="utf-8")
    fallback = tmp_path / "fallback.csv"
    fallback.write_text("OID_;UJAHR\n2;2023\n", encoding="utf-8")

    def successful_download(candidate, target_dir):
        return official_file

    selected = resolve_source(
        official=SourceCandidate(name="Official", url_or_path="https://example.test/official.csv", source_type="official_download"),
        fallback=SourceCandidate(name="Fallback", url_or_path=str(fallback), source_type="opal_fallback"),
        cache_dir=tmp_path,
        download_func=successful_download,
    )

    assert selected.source_type == "official_download"
    assert selected.local_path == str(official_file)
    assert selected.warning == ""
