from datetime import datetime
from enum import Enum
from typing import Self

from fastapi import UploadFile
from pydantic import model_validator
from sqlmodel import Field, Relationship, SQLModel


class ItemType(str, Enum):
    paper = "paper"
    plastic = "plastic"
    glass = "glass"
    metal = "metal"
    unknown = "unknown"


class BoundingBoxBase(SQLModel):
    item_type: ItemType
    x_left: int = Field(ge=0)
    x_right: int = Field(ge=0)
    y_top: int = Field(ge=0)
    y_bottom: int = Field(ge=0)

    @model_validator(mode="after")
    def check_coordinates(self) -> Self:
        if not self.x_left < self.x_right:
            raise ValueError("x_left must be less than x_right")

        if not self.y_top < self.y_bottom:
            raise ValueError("y_top must be less than y_bottom")

        return self


class BoundingBoxRequest(BoundingBoxBase):
    pass


class BoundingBoxResponse(BoundingBoxBase):
    pass


class BoundingBox(BoundingBoxBase, table=True):  # type: ignore
    id: int | None = Field(default=None, primary_key=True)

    item_id: int = Field(foreign_key="item.id")
    item: "Item" = Relationship(back_populates="bounding_boxes")

    def into_response(self) -> BoundingBoxResponse:
        return BoundingBoxResponse(**self.model_dump())

    @staticmethod
    def from_request(
        bb: BoundingBoxRequest, item_id: str | None = None
    ) -> "BoundingBox":
        """Intended for use only when creating item"""
        return BoundingBox(
            **bb.model_dump(),
            item_id=item_id,
        )


class ItemBase(SQLModel):
    user_id: str
    created_at: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class ItemCreate(ItemBase):
    photo: UploadFile
    bounding_boxes_json: (
        str  # JSON-encoded list[BoundingBoxRequest], str due to a bug in swaggerui
    )


class ItemResponse(ItemBase):
    id: int = Field(default=None, primary_key=True)
    photo_id: str
    user_id: str
    uploaded_at: datetime
    bounding_boxes: list[BoundingBoxResponse]


class Item(ItemBase, table=True):  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    photo_id: str
    uploaded_at: datetime
    bounding_boxes: list[BoundingBox] = Relationship(back_populates="item")

    def into_response(self) -> ItemResponse:
        return ItemResponse(
            **self.model_dump(),
            bounding_boxes=[bb.into_response() for bb in self.bounding_boxes],
        )
