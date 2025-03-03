from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.user import User
    from core.models.item import Item

from sqlmodel import Field, Relationship, SQLModel


class MessageBase(SQLModel):
    message: str
    timestamp: datetime


class MessageRequest(MessageBase):
    item_id: int


class MessageResponse(MessageBase):
    id: int
    author_id: str


class Message(MessageBase, table=True):  # type: ignore
    id: int | None = Field(default=None, primary_key=True)

    author_id: str = Field(foreign_key="user.id")
    author: "User" = Relationship(back_populates="messages")

    item_id: int = Field(foreign_key="item.id", index=True)
    item: "Item" = Relationship(back_populates="messages")

    def into_response(self) -> MessageResponse:
        return MessageResponse(**self.model_dump())
