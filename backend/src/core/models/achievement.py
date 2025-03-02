from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.user import User

from sqlmodel import Field, Relationship, SQLModel


class AchievementUserLink(SQLModel, table=True):  # type: ignore
    achievement_id: int | None = Field(
        default=None, foreign_key="achievement.id", primary_key=True
    )
    user_id: str = Field(foreign_key="user.id", primary_key=True)


class AchievementBase(SQLModel):
    name: str
    description: str


class AchievementResponse(AchievementBase):
    id: int


class UserAchievementResponse(AchievementBase):
    id: int
    unlocked: bool


class Achievement(AchievementBase, table=True):  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    unlocked_by: list["User"] = Relationship(
        back_populates="achievements", link_model=AchievementUserLink
    )

    def into_response(self) -> AchievementResponse:
        return AchievementResponse(**self.model_dump())
