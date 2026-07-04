from apps.importer.parsers.unfallatlas import parse_unfallatlas_csv


def test_parse_unfallatlas_semicolon_decimal_comma(tmp_path):
    csv_file = tmp_path / "accidents.csv"
    csv_file.write_text(
        "OID_;UIDENTSTLAE;ULAND;UREGBEZ;UKREIS;UGEMEINDE;UJAHR;UMONAT;USTUNDE;UWOCHENTAG;UKATEGORIE;UART;UTYP1;ULICHTVERH;IstStrassenzustand;IstRad;IstPKW;IstFuss;IstKrad;IstGkfz;IstSonstige;XGCSWGS84;YGCSWGS84\n"
        "1;01230519134013042023;01;0;02;000;2023;05;22;6;3;5;2;2;0;0;1;0;0;0;0;10,148875393000026;54,306951053000034\n",
        encoding="utf-8-sig",
    )

    rows = list(parse_unfallatlas_csv(csv_file))

    assert rows[0]["source_event_id"] == "01230519134013042023"
    assert rows[0]["source_state"] == "01"
    assert rows[0]["source_regbez"] == "0"
    assert rows[0]["source_district"] == "02"
    assert rows[0]["source_municipality"] == "000"
    assert rows[0]["year"] == 2023
    assert rows[0]["is_car"] is True
    assert rows[0]["longitude"] == "10.148875393000026"


def test_parse_unfallatlas_zip_with_csv(tmp_path):
    from zipfile import ZipFile

    zip_file = tmp_path / "Unfallorte2023_EPSG25832_CSV.zip"
    csv_content = (
        "OID_;UIDENTSTLAE;ULAND;UREGBEZ;UKREIS;UGEMEINDE;UJAHR;UMONAT;USTUNDE;UWOCHENTAG;UKATEGORIE;UART;UTYP1;ULICHTVERH;IstStrassenzustand;IstRad;IstPKW;IstFuss;IstKrad;IstGkfz;IstSonstige;XGCSWGS84;YGCSWGS84\n"
        "1;zip-event;11;0;00;000;2023;05;14;2;3;5;2;0;0;0;1;0;0;0;0;13,40500000;52,52000000\n"
    )
    with ZipFile(zip_file, "w") as archive:
        archive.writestr("accidents.csv", csv_content)

    rows = list(parse_unfallatlas_csv(zip_file))

    assert rows[0]["source_event_id"] == "zip-event"
    assert rows[0]["longitude"] == "13.40500000"


def test_parse_unfallatlas_zip_with_txt_data_file(tmp_path):
    from zipfile import ZipFile

    zip_file = tmp_path / "Unfallorte2021_EPSG25832_CSV.zip"
    txt_content = (
        "OID_;UIDENTSTLAE;ULAND;UREGBEZ;UKREIS;UGEMEINDE;UJAHR;UMONAT;USTUNDE;UWOCHENTAG;UKATEGORIE;UART;UTYP1;ULICHTVERH;IstStrassenzustand;IstRad;IstPKW;IstFuss;IstKrad;IstGkfz;IstSonstige;XGCSWGS84;YGCSWGS84\n"
        "1;txt-event;01;0;02;000;2021;05;14;2;3;5;2;0;0;0;1;0;0;0;0;10,148875393000026;54,306951053000034\n"
    )
    with ZipFile(zip_file, "w") as archive:
        archive.writestr("Unfallorte2021_EPSG25832_CSV/schema.ini", "unused")
        archive.writestr("Unfallorte2021_EPSG25832_CSV/Unfallorte_2021_LinRef.txt", txt_content)

    rows = list(parse_unfallatlas_csv(zip_file))

    assert rows[0]["source_event_id"] == "txt-event"
    assert rows[0]["year"] == 2021
