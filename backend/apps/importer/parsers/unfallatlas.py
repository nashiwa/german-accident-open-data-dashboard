import csv
from pathlib import Path
from zipfile import ZipFile


DATA_FILE_SUFFIXES = (".csv", ".txt")


def _decimal(value: str) -> str:
    return value.replace(",", ".").strip()


def _flag(value: str) -> bool:
    return str(value).strip() == "1"


def _optional_int(value: str):
    value = str(value or "").strip()
    return int(value) if value else None


def _iter_csv_rows(handle):
    reader = csv.DictReader(handle, delimiter=";")
    for row in reader:
        yield {
            "source_event_id": row.get("UIDENTSTLAE") or row.get("OID_") or row.get("OBJECTID"),
            "source_state": row.get("ULAND", "").zfill(2),
            "source_regbez": row.get("UREGBEZ", "").zfill(1),
            "source_district": row.get("UKREIS", "").zfill(2),
            "source_municipality": row.get("UGEMEINDE", "").zfill(3),
            "year": int(row["UJAHR"]),
            "month": int(row["UMONAT"]),
            "hour": _optional_int(row.get("USTUNDE")),
            "weekday": _optional_int(row.get("UWOCHENTAG")),
            "category": row.get("UKATEGORIE", ""),
            "accident_type": row.get("UART", ""),
            "light_condition": row.get("ULICHTVERH", ""),
            "road_condition": row.get("IstStrassenzustand") or row.get("USTRZUSTAND", ""),
            "is_bicycle": _flag(row.get("IstRad", "0")),
            "is_car": _flag(row.get("IstPKW", "0")),
            "is_pedestrian": _flag(row.get("IstFuss", "0")),
            "is_motorcycle": _flag(row.get("IstKrad", "0")),
            "is_goods_vehicle": _flag(row.get("IstGkfz", "0")),
            "is_other": _flag(row.get("IstSonstige", "0")),
            "longitude": _decimal(row["XGCSWGS84"]),
            "latitude": _decimal(row["YGCSWGS84"]),
        }


def parse_unfallatlas_csv(path: Path):
    path = Path(path)
    if path.suffix.lower() == ".zip":
        with ZipFile(path) as archive:
            data_names = [name for name in archive.namelist() if name.lower().endswith(DATA_FILE_SUFFIXES)]
            if not data_names:
                raise ValueError(f"No CSV or TXT data file found in {path}")
            with archive.open(data_names[0]) as raw_handle:
                text = (line.decode("utf-8-sig") for line in raw_handle)
                yield from _iter_csv_rows(text)
        return

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        yield from _iter_csv_rows(handle)
