from sqlmodel import Field, SQLModel
from data_enums import TrashType


# Common public data about Items
class ItemBase(SQLModel):
    type: TrashType = Field(default=TrashType.other)
    latitude: float = Field()
    longitude: float = Field()
    

# Data about Items stored in db
class Item(ItemBase, table=True):
    id: int = Field(default=None, primary_key=True)


# Data returned about an item
class ItemPublic(ItemBase):
    id: int


# Data needed to add a new Item
class ItemCreate(ItemBase):
    pass
