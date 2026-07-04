# German Accident Open Data Dashboard

A full-stack open data project for exploring German road accident statistics. The application combines a Django REST API, a MariaDB-backed data model, an Angular dashboard, and local fallback CSV files so the project can be demonstrated even when the official download source is unavailable.

## What It Does

- Imports Unfallatlas accident point data with an official-source-first, local-fallback-second workflow.
- Stores accident facts, region metadata, source records, and import run provenance in a normalized database schema.
- Exposes REST endpoints for examiner-style questions, accident aggregates, rankings, source metadata, and API documentation.
- Provides an Angular dashboard for mandatory question answers, accident exploration, rankings, map preview, and import/source visibility.

## Repository Structure

```text
.
|-- backend/              Django REST API, import command, models, tests
|-- data/                 Public fallback CSV data used by the importer
|-- frontend/             Angular dashboard application
|-- DATA_SOURCES.md       Public source and license attribution
|-- docker-compose.yml    Local backend/frontend orchestration
|-- .env.example          Local development environment defaults
`-- .gitignore            Local, generated, duplicate, and internal files excluded from Git
```

The `docs/` folder is intentionally ignored because it contains local planning and submission notes. Public data attribution is kept in `DATA_SOURCES.md`.

## Main Technologies

- Backend: Django, Django REST Framework, drf-spectacular, MySQL/MariaDB
- Frontend: Angular, RxJS, Chart.js
- Data processing: Python, pandas, shapely, requests
- Development: Docker Compose, pytest, Angular CLI

## Quick Start

1. Copy `.env.example` to `.env` if you want to override local settings.
2. Start the supporting services you need. The current compose file runs the backend and frontend containers and expects MySQL to be reachable through the configured host.
3. Run database migrations from `backend/`.
4. Import accident data using the Django management command.
5. Start the API and dashboard.

Typical local commands:

```powershell
cd backend
python manage.py migrate
python manage.py import_accident_platform --years 2023
python manage.py runserver 127.0.0.1:8000
```

```powershell
cd frontend
npm install
npm start -- --host 127.0.0.1 --port 4200
```

Open:

```text
http://127.0.0.1:4200/
```

Useful API URLs:

```text
http://127.0.0.1:8000/api/health/
http://127.0.0.1:8000/api/questions/mandatory/
http://127.0.0.1:8000/api/docs/
http://127.0.0.1:8000/api/schema/
```

## Data Notes

The fallback CSV files under `data/accident_fallback_data_1/` are public data snapshots used for reproducible local imports. See `DATA_SOURCES.md` for provider and license attribution.

## Development Checks

Backend:

```powershell
cd backend
pytest
python manage.py test
```

Frontend:

```powershell
cd frontend
npm test -- --watch=false
npm run build
```

## Git Hygiene

The repository ignores local environments, caches, build output, SQLite files, internal docs, and duplicate data folders. The first public branch is `main`.
