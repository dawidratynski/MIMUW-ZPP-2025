from core.models.item import ItemBase


def test_example():
    item = ItemBase(latitude=12, longitude=-12)
    assert item is not None
