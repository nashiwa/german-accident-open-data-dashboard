import pytest

from apps.regions.models import Region


@pytest.mark.django_db
def test_region_parent_hierarchy():
    state = Region.objects.create(ags="14", name="Sachsen", level=Region.Level.STATE)
    district = Region.objects.create(
        ags="14612",
        name="Dresden",
        level=Region.Level.DISTRICT,
        parent=state,
        state_code="SN",
        state_name="Sachsen",
    )

    assert district.parent == state
    assert str(district) == "Dresden (district)"
