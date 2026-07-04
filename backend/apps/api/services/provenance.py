from apps.catalog.models import ImportRun


def latest_successful_import_provenance(limit=5):
    runs = (
        ImportRun.objects.select_related("source")
        .filter(status=ImportRun.Status.SUCCESS)
        .order_by("-started_at")[:limit]
    )
    return [
        {
            "source": run.source.name,
            "source_type": run.source.source_type,
            "url_or_path": run.source.url_or_path,
            "licence": run.source.licence,
            "provider": run.source.provider,
            "retrieved_at": run.started_at.isoformat() if run.started_at else None,
            "import_run_id": run.id,
            "rows_read": run.rows_read,
            "warnings": run.warnings,
        }
        for run in runs
    ]
