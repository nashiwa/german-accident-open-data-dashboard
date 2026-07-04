from itertools import islice
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.catalog.models import ImportRun, Source
from apps.importer.parsers.unfallatlas import parse_unfallatlas_csv
from apps.importer.services.loaders import load_accidents
from apps.importer.services.plausibility import check_accident_rows
from apps.importer.source_resolver import SourceCandidate, resolve_source


DEFAULT_UNFALLATLAS_2023_URL = "https://www.opengeodata.nrw.de/produkte/transport_verkehr/unfallatlas/Unfallorte2023_EPSG25832_CSV.zip"


def _source_url_for_year(template_url, year):
    return template_url.replace("2023", str(year))


def _fallback_path_for_year(project_root, configured_fallback, year):
    if year == 2023:
        return configured_fallback

    fallback_dir = project_root / "data" / "accident_fallback_data_1"
    exact = fallback_dir / f"accident_per_location_{year}.csv"
    if exact.exists():
        return str(exact)

    candidates = sorted(fallback_dir.glob(f"accident_per_location_{year}*.csv"))
    if candidates:
        return str(candidates[0])

    return str(exact)


class Command(BaseCommand):
    help = "Import accident platform data using official source first and OPAL fallback second."

    def add_arguments(self, parser):
        project_root = settings.BASE_DIR.parent
        parser.add_argument("--official-accidents-2023-url", default=DEFAULT_UNFALLATLAS_2023_URL)
        parser.add_argument(
            "--accidents-2023-fallback",
            default=str(project_root / "data" / "accident_fallback_data_1" / "accident_per_location_2023.csv"),
        )
        parser.add_argument("--cache-dir", default=str(project_root / ".cache" / "sources"))
        parser.add_argument("--limit", type=int, default=None)
        parser.add_argument("--years", nargs="+", type=int, default=[2023])

    def handle(self, *args, **options):
        project_root = settings.BASE_DIR.parent
        total_rows = 0
        for year in options["years"]:
            total_rows += self._import_year(project_root=project_root, year=year, options=options)

        self.stdout.write(self.style.SUCCESS(f"Imported {total_rows} accident rows across {len(options['years'])} year(s)"))

    def _import_year(self, *, project_root, year, options):
        official_url = _source_url_for_year(options["official_accidents_2023_url"], year)
        fallback_path = _fallback_path_for_year(project_root, options["accidents_2023_fallback"], year)
        resolved = resolve_source(
            official=SourceCandidate(
                name=f"Unfallatlas {year}",
                url_or_path=official_url,
                source_type=Source.SourceType.OFFICIAL_DOWNLOAD,
            ),
            fallback=SourceCandidate(
                name=f"OPAL Unfallatlas {year} fallback",
                url_or_path=fallback_path,
                source_type=Source.SourceType.OPAL_FALLBACK,
            ),
            cache_dir=Path(options["cache_dir"]),
        )

        source, _ = Source.objects.update_or_create(
            name=resolved.name,
            defaults={
                "source_type": resolved.source_type,
                "url_or_path": resolved.url_or_path,
                "provider": "Statistische Aemter / TU Chemnitz OPAL",
                "licence": "Datenlizenz Deutschland Namensnennung 2.0",
                "description": "Accident point data for the DBW project ETL.",
            },
        )
        run = ImportRun.objects.create(
            source=source,
            status=ImportRun.Status.STARTED,
            warnings=[resolved.warning] if resolved.warning else [],
        )

        try:
            parsed_rows = parse_unfallatlas_csv(Path(resolved.local_path))
            rows = list(islice(parsed_rows, options["limit"])) if options["limit"] else list(parsed_rows)
            warnings = [*run.warnings, *check_accident_rows(rows)]
            result = load_accidents(rows, source, run)
            run.status = ImportRun.Status.SUCCESS
            run.finished_at = timezone.now()
            run.rows_read = len(rows)
            run.rows_inserted = result.inserted
            run.rows_updated = result.updated
            run.warnings = warnings
            run.save()
        except Exception as exc:
            run.status = ImportRun.Status.FAILED
            run.finished_at = timezone.now()
            run.warnings = [*run.warnings, str(exc)]
            run.save()
            raise

        self.stdout.write(self.style.SUCCESS(f"Imported {len(rows)} accident rows for {year} from {resolved.source_type}"))
        return len(rows)
