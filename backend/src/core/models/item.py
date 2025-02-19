from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


class ItemType(str, Enum):
    paper = "paper"
    plastic = "plastic"
    glass = "glass"
    metal = "metal"
    unknown = "unknown"


class PhotoPixel(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)


class BoundingBox(SQLModel, table=True):  # type: ignore
    id: int = Field(default=None, primary_key=True)

    item_id: int = Field(foreign_key="item.id")
    item: "Item" = Relationship(back_populates="bounding_boxes")

    type: ItemType

    left_upper_corner_x: int = Field(ge=0)
    left_upper_corner_y: int = Field(ge=0)
    right_bottom_corner_x: int = Field(ge=0)
    right_bottom_corner_y: int = Field(ge=0)

    def into_response_model(self) -> tuple[PhotoPixel, PhotoPixel, ItemType]:
        return (
            PhotoPixel(x=self.left_upper_corner_x, y=self.left_upper_corner_y),
            PhotoPixel(x=self.right_bottom_corner_x, y=self.right_bottom_corner_y),
            self.type,
        )


class ItemCreate(BaseModel):
    user_id: str
    created_at: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    boundng_boxes: list[tuple[PhotoPixel, PhotoPixel, ItemType]]


class ItemResponse(BaseModel):
    id: int = Field(default=None, primary_key=True)
    photo_id: str
    user_id: str

    created_at: datetime
    uploaded_at: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    boundng_boxes: list[tuple[PhotoPixel, PhotoPixel, ItemType]]


class Item(SQLModel, table=True):  # type: ignore
    id: int = Field(default=None, primary_key=True)
    photo_id: str
    user_id: str

    created_at: datetime
    uploaded_at: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    bounding_boxes: list[BoundingBox] = Relationship(back_populates="item")

    def into_response_model(self) -> ItemResponse:
        return ItemResponse(
            **self,
            bounding_boxes=[bb.into_response_model() for bb in self.bounding_boxes]
        )
