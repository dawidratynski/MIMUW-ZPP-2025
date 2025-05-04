from sqlmodel import Field, Relationship, SQLModel

from core.db import SessionDep
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


def ensure_user(user_id, session: SessionDep) -> User:
    """
    Get an existing user or create a new user with given id
    """
    if user := session.get(User, user_id):
        return user
    else:
        user = User(id=user_id)
        saved_user = User.model_validate(user)
        session.add(saved_user)
        session.commit()
        session.refresh(saved_user)
        return saved_user
