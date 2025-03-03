from sqlmodel import Field, Relationship, SQLModel

from core.models.achievement import Achievement, AchievementUserLink
from core.models.message import Message


class UserBase(SQLModel):
    id: str = Field(primary_key=True)


class UserResponse(UserBase):
    pass


class User(UserBase, table=True):  # type: ignore
    achievements: list["Achievement"] = Relationship(
        back_populates="unlocked_by", link_model=AchievementUserLink
    )
    messages: list["Message"] = Relationship(back_populates="author")

    def into_response(self) -> UserResponse:
        return UserResponse(**self.model_dump())
