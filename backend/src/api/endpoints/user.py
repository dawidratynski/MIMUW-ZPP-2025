from fastapi import APIRouter, HTTPException, Security
from sqlmodel import select

from core.auth import VerifyToken
from core.db import SessionDep
from core.models.achievement import Achievement, UserAchievementResponse
from core.models.user import User, UserResponse
from core.utils import validate_user_id

auth = VerifyToken()

router = APIRouter(prefix="/users")


@router.post("/{user_id}/register", response_model=UserResponse)
def register_user(
    user_id: str,
    session: SessionDep,
    auth_result: str = Security(auth.verify),
):
    """
    Register user in database if not already present.
    """

    validate_user_id(auth_result, user_id)

    if user := session.get(User, user_id):
        return user.into_response()

    user = User(id=user_id, achievements=[])
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
        raise HTTPException(status_code=404, detail="User not found")

    if only_unlocked:
        return [
            UserAchievementResponse(**achievement.model_dump(), unlocked=True)
            for achievement in user.achievements
        ]
    else:
        all_achievements = session.exec(select(Achievement)).all()
        return [
            UserAchievementResponse(
                **achievement.model_dump(), unlocked=(achievement in user.achievements)
            )
            for achievement in all_achievements
        ]


@router.get(
    "/{user_id}/achievements/{achievement_id}", response_model=UserAchievementResponse
)
def get_user_achievement(user_id: str, achievement_id: int, session: SessionDep):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    achievement = session.get(Achievement, achievement_id)

    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    unlocked = achievement in user.achievements

    return UserAchievementResponse(**achievement.model_dump(), unlocked=unlocked)


@router.post(
    "/{user_id}/achievements/{achievement_id}/unlock",
    response_model=UserAchievementResponse,
)
def unlock_achievement(
    user_id: str,
    achievement_id: int,
    session: SessionDep,
    auth_result: str = Security(auth.verify),
):
    validate_user_id(auth_result, user_id)

    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    achievement = session.get(Achievement, achievement_id)

    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    if achievement not in user.achievements:
        user.achievements.append(achievement)
        session.commit()

    return UserAchievementResponse(**achievement.model_dump(), unlocked=True)
