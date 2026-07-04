import pytest

from apps.importer.services.region_codes import assign_regions_from_source_codes
from apps.regions.models import Region


@pytest.mark.django_db
def test_assign_regions_from_source_codes_creates_state_district_and_municipality():
    assigned = assign_regions_from_source_codes({
        "source_state": "14",
        "source_regbez": "6",
        "source_district": "12",
        "source_municipality": "000",
    })

    assert assigned["state_region"].state_code == "SN"
    assert assigned["state_region"].name == "Sachsen"
    assert assigned["district_region"].ags == "14612"
    assert Region.objects.filter(ags="14612", level=Region.Level.DISTRICT).exists()
