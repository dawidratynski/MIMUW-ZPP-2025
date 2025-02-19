# TODO: Rework

from sqlmodel import Field, SQLModel

from core.models.types import TrashType


# Common public data about Items
class ItemBase(SQLModel):
    type: TrashType = Field(default=TrashType.other)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


# Data about Items stored in db
# TODO: mypy raises error without 'type: ignore' - check if this correct
class Item(ItemBase, table=True):  # type: ignore
    id: int = Field(default=None, primary_key=True)


# Data returned about an item
class ItemPublic(ItemBase):
    id: int


# Data needed to add a new Item
class ItemCreate(ItemBase):
    pass
