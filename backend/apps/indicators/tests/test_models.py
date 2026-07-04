from decimal import Decimal

import pytest

from apps.catalog.models import ImportRun, Source
from apps.indicators.models import Indicator, IndicatorValue
from apps.regions.models import Region


@pytest.mark.django_db
def test_indicator_value_belongs_to_region_and_year():
    source = Source.objects.create(
        name="GV-ISys",
        source_type=Source.SourceType.OFFICIAL_DOWNLOAD,
        url_or_path="https://example.test/gvisys.csv",
        provider="Destatis",
        licence="official open data",
    )
    run = ImportRun.objects.create(source=source, status=ImportRun.Status.SUCCESS)
    region = Region.objects.create(ags="14", name="Sachsen", level=Region.Level.STATE)
    indicator = Indicator.objects.create(code="population", name="Population", unit="persons", source_system="GV-ISys")

    value = IndicatorValue.objects.create(
        region=region,
        indicator=indicator,
        year=2023,
        value=Decimal("4086152"),
        source=source,
        import_run=run,
    )

    assert value.value == Decimal("4086152")
