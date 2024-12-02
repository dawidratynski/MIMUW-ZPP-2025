from sqlmodel import Field, SQLModel

class Item(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    image_id: int = Field(default=None)
