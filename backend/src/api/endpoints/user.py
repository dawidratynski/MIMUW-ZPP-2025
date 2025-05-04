from fastapi import APIRouter, HTTPException, Security
from sqlmodel import select

from core.auth import VerifyUserID
from core.db import SessionDep
from core.models.achievement import (
    Achievement,
    AchievementUserLink,
    UserAchievementResponse,
)
from core.models.user import User, UserResponse, ensure_user
from core.utils import validate_user_id

auth = VerifyUserID()

router = APIRouter(prefix="/users")


@router.post("/{user_id}/register", response_model=UserResponse, deprecated=True)
def register_user(
    user_id: str,
    session: SessionDep,
    auth_user_id: str = Security(auth),
):
    """
    Deprecated: User is now created automatically if not present in the db

    Register user in database if not already present.
    """

    validate_user_id(auth_user_id, user_id)

    if user := session.get(User, user_id):
        return user.into_response()

    user = User(id=user_id)
    saved_user = User.model_validate(user)
    session.add(saved_user)
    session.commit()
    session.refresh(saved_user)
    return saved_user.into_response()


@router.get("/{user_id}/achievements", response_model=list[UserAchievementResponse])
def list_user_achievements(
    user_id: str,
    session: SessionDep,
    only_unlocked: bool = True,
):
    user = session.get(User, user_id)

    if not user:
        return []

    if only_unlocked:
        result = []
        for achievement in user.achievements:
            link = session.exec(
                select(AchievementUserLink).where(
                    AchievementUserLink.user_id == user.id,
                    AchievementUserLink.achievement_id == achievement.id,
                )
            ).first()
            result.append(
                UserAchievementResponse(
                    **achievement.model_dump(),
                    unlocked=True,
                    unlocked_at=link.unlocked_at if link else None,
                )
            )
        return result
    else:
        all_achievements = session.exec(select(Achievement)).all()
        result = []
        for achievement in all_achievements:
            if achievement in user.achievements:
                link = session.exec(
                    select(AchievementUserLink).where(
                        AchievementUserLink.user_id == user.id,
                        AchievementUserLink.achievement_id == achievement.id,
                    )
                ).first()
                unlocked = True
                unlocked_at = link.unlocked_at if link else None
            else:
                unlocked = False
                unlocked_at = None

            result.append(
                UserAchievementResponse(
                    **achievement.model_dump(),
                    unlocked=unlocked,
                    unlocked_at=unlocked_at,
                )
            )
        return result


@router.get(
    "/{user_id}/achievements/{achievement_id}", response_model=UserAchievementResponse
)
def get_user_achievement(user_id: str, achievement_id: int, session: SessionDep):
    user = session.get(User, user_id)
    achievement = session.get(Achievement, achievement_id)

    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    unlocked = user is not None and achievement in user.achievements
    unlocked_at = None

    if unlocked:
        link = session.exec(
            select(AchievementUserLink).where(
                AchievementUserLink.user_id == user.id,
                AchievementUserLink.achievement_id == achievement.id,
            )
        ).first()
        unlocked_at = link.unlocked_at if link else None

    return UserAchievementResponse(
        **achievement.model_dump(),
        unlocked=unlocked,
        unlocked_at=unlocked_at,
    )


@router.post(
    "/{user_id}/achievements/{achievement_id}/unlock",
    response_model=UserAchievementResponse,
)
def unlock_achievement(
    user_id: str,
    achievement_id: int,
    session: SessionDep,
    auth_user_id: str = Security(auth),
):
    validate_user_id(auth_user_id, user_id)

    user = ensure_user(user_id, session)

    achievement = session.get(Achievement, achievement_id)

    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    if achievement not in user.achievements:
        user.achievements.append(achievement)
        session.commit()
        session.refresh(achievement)
        session.refresh(user)

    link = session.exec(
        select(AchievementUserLink).where(
            AchievementUserLink.user_id == user.id,
            AchievementUserLink.achievement_id == achievement.id,
        )
    ).first()

    return UserAchievementResponse(
        **achievement.model_dump(),
        unlocked=True,
        unlocked_at=link.unlocked_at if link else None,
    )
