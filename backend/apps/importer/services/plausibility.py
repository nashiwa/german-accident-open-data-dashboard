def check_accident_rows(rows):
    warnings = []
    for index, row in enumerate(rows, start=1):
        if not row.get("longitude") or not row.get("latitude"):
            warnings.append(f"row {index} has missing coordinates")
        year = row.get("year")
        if year and (year < 2016 or year > 2030):
            warnings.append(f"row {index} has suspicious year {year}")
        if not row.get("source_event_id"):
            warnings.append(f"row {index} has missing source event id")
    return warnings
