# Backend

Django REST backend for the German accident open data dashboard. It owns the database schema, data import workflow, source provenance records, and JSON API consumed by the Angular frontend.

## Responsibilities

- Model normalized accident, region, indicator, source, and import-run data.
- Resolve accident data from the official Unfallatlas download first, then local fallback CSV files.
- Parse and load accident CSV rows into MariaDB/MySQL.
- Run plausibility checks and preserve import metadata.
- Serve REST endpoints for aggregates, rankings, mandatory questions, source metadata, and OpenAPI documentation.

## Layout

```text
backend/
|-- apps/
|   |-- accidents/        Accident fact model
|   |-- api/              REST serializers, views, query services, URLs
|   |-- catalog/          Source and import-run provenance models
|   |-- core/             Health endpoint
|   |-- importer/         Source resolver, parsers, loaders, import command
|   |-- indicators/       Optional indicator/rate model
|   `-- regions/          Region hierarchy model
|-- config/               Django settings and root URLs
|-- manage.py
|-- pytest.ini
`-- requirements.txt
```

## Environment

Settings are loaded from `.env` in the project root. Use `.env.example` as the template. Important variables include:

```text
MYSQL_DATABASE
MYSQL_USER
MYSQL_PASSWORD
MYSQL_HOST
MYSQL_PORT
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
```

The local defaults are for development only.

## Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
```

## Import Data

The importer tries the official Unfallatlas URL first. If the download fails, it uses the fallback CSVs under `../data/accident_fallback_data_1/`.

```powershell
python manage.py import_accident_platform --years 2023
```

Useful options:

```powershell
python manage.py import_accident_platform --years 2021 2023
python manage.py import_accident_platform --years 2023 --limit 1000
```

## Run

```powershell
python manage.py runserver 127.0.0.1:8000
```

Useful endpoints:

```text
/api/health/
/api/regions/
/api/accidents/
/api/aggregates/accidents/
/api/aggregates/rates/
/api/metadata/sources/
/api/import-runs/
/api/questions/mandatory/
/api/docs/
/api/schema/
```

## Checks

```powershell
pytest
python manage.py test
```

`pytest` runs the project test suite. `python manage.py test` is also useful for Django system checks, but the current tests are written for pytest.
