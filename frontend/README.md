# Frontend

Angular dashboard for the German accident open data project. It consumes the Django API and presents examiner-ready answers, accident filters, rankings, source metadata, and a small spatial preview.

## Responsibilities

- Show mandatory question answers from the backend API.
- Let users filter accident aggregates by year, state, and participant type.
- Display ranking/rate views for comparing regions.
- Provide a map-style preview of accident points.
- Show source and import-run metadata so answers can be traced back to their data origin.

## Layout

```text
frontend/
|-- src/app/
|   |-- core/                         API service and shared API types
|   |-- features/
|   |   |-- accident-explorer/        Aggregate filters and results
|   |   |-- examiner-questions/       Mandatory question screen
|   |   |-- map-view/                 Accident point preview
|   |   |-- rates-rankings/           Rate and ranking view
|   |   `-- sources-imports/          Source/import metadata view
|   |-- app.routes.ts                 Dashboard routes
|   `-- app.*                         Shell component
|-- angular.json
|-- package.json
`-- tsconfig*.json
```

## Routes

```text
/             Mandatory questions
/explorer     Accident explorer
/rankings     Rates and rankings
/map          Accident point preview
/sources      Sources and import runs
```

## Setup

```powershell
cd frontend
npm install
```

## Run Locally

```powershell
npm start -- --host 127.0.0.1 --port 4200
```

Open:

```text
http://127.0.0.1:4200/
```

The Django API should be running at:

```text
http://127.0.0.1:8000/api
```

## Checks

```powershell
npm test -- --watch=false
npm run build
npm audit --omit=dev
```
