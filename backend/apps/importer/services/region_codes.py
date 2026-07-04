from apps.regions.models import Region


STATE_NAMES = {
    "01": ("SH", "Schleswig-Holstein"),
    "02": ("HH", "Hamburg"),
    "03": ("NI", "Niedersachsen"),
    "04": ("HB", "Bremen"),
    "05": ("NW", "Nordrhein-Westfalen"),
    "06": ("HE", "Hessen"),
    "07": ("RP", "Rheinland-Pfalz"),
    "08": ("BW", "Baden-Wuerttemberg"),
    "09": ("BY", "Bayern"),
    "10": ("SL", "Saarland"),
    "11": ("BE", "Berlin"),
    "12": ("BB", "Brandenburg"),
    "13": ("MV", "Mecklenburg-Vorpommern"),
    "14": ("SN", "Sachsen"),
    "15": ("ST", "Sachsen-Anhalt"),
    "16": ("TH", "Thueringen"),
}


def assign_regions_from_source_codes(row):
    state_key = row.get("source_state", "")
    regbez = row.get("source_regbez", "")
    district = row.get("source_district", "")
    municipality = row.get("source_municipality", "")
    state_code, state_name = STATE_NAMES.get(state_key, (state_key, f"State {state_key}"))

    state_region, _ = Region.objects.get_or_create(
        ags=state_key,
        defaults={
            "name": state_name,
            "level": Region.Level.STATE,
            "state_code": state_code,
            "state_name": state_name,
        },
    )
    assigned = {"state_region": state_region}

    if regbez and district and district != "00":
        district_ags = f"{state_key}{regbez}{district}"
        district_region, _ = Region.objects.get_or_create(
            ags=district_ags,
            defaults={
                "name": f"District {district_ags}",
                "level": Region.Level.DISTRICT,
                "parent": state_region,
                "state_code": state_code,
                "state_name": state_name,
            },
        )
        assigned["district_region"] = district_region

        if municipality and municipality != "000":
            municipality_ags = f"{district_ags}{municipality}"
            municipality_region, _ = Region.objects.get_or_create(
                ags=municipality_ags,
                defaults={
                    "name": f"Municipality {municipality_ags}",
                    "level": Region.Level.MUNICIPALITY,
                    "parent": district_region,
                    "state_code": state_code,
                    "state_name": state_name,
                },
            )
            assigned["municipality_region"] = municipality_region

    return assigned
