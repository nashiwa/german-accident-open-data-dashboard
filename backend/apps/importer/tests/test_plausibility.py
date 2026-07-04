from apps.importer.services.plausibility import check_accident_rows


def test_check_accident_rows_reports_missing_coordinates():
    warnings = check_accident_rows([
        {"source_event_id": "1", "year": 2023, "longitude": "", "latitude": "52.5"},
    ])

    assert warnings == ["row 1 has missing coordinates"]


def test_check_accident_rows_reports_suspicious_year_and_missing_id():
    warnings = check_accident_rows([
        {"source_event_id": "", "year": 2035, "longitude": "13.4", "latitude": "52.5"},
    ])

    assert warnings == ["row 1 has suspicious year 2035", "row 1 has missing source event id"]
