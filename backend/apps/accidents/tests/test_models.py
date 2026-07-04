from decimal import Decimal

import pytest

from apps.accidents.models import Accident
from apps.catalog.models import ImportRun, Source
from apps.regions.models import Region


@pytest.mark.django_db
def test_accident_stores_region_assignments():
    source = Source.objects.create(
        name="Unfallatlas 2023",
        source_type=Source.SourceType.OPAL_FALLBACK,
        url_or_path="/data/accident_per_location_2023.csv",
        provider="TU Chemnitz OPAL",
        licence="course fallback data",
    )
    run = ImportRun.objects.create(source=source, status=ImportRun.Status.SUCCESS)
    state = Region.objects.create(ags="11", name="Berlin", level=Region.Level.STATE, state_code="BE")
    accident = Accident.objects.create(
        source_event_id="event-1",
        year=2023,
        month=5,
        hour=14,
        weekday=2,
        category="3",
        is_pedestrian=True,
        longitude=Decimal("13.40500000"),
        latitude=Decimal("52.52000000"),
        state_region=state,
        source=source,
        import_run=run,
    )

    assert accident.state_region == state
    assert accident.is_pedestrian is True
