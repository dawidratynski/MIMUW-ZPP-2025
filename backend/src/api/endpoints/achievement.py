from fastapi import APIRouter, HTTPException, Security
from sqlmodel import select

from core.auth import VerifyToken
from core.db import SessionDep
from core.models.achievement import (
    Achievement,
    AchievementRequest,
    AchievementResponse,
    UserAchievementResponse,
)
from core.models.user import User
from core.utils import validate_user_id

auth = VerifyToken()

router = APIRouter(prefix="/achievement")


@router.get("/list", response_model=list[AchievementResponse])
def list_all_achievements(session: SessionDep):
    achievements = session.exec(select(Achievement)).all()
    return [achievement.into_response() for achievement in achievements]


@router.get("/{achievement_id}", response_model=AchievementResponse)
def get_achievement(achievement_id: int, session: SessionDep):
    achievement = session.get(Achievement, achievement_id)

    if not achievement:
        raise HTTPException(
            status_code=404, detail="No achievement with given id found"
        )

    return achievement.into_response()


@router.get("/user/{user_id}", response_model=list[UserAchievementResponse])
def list_unlocked_achievements(user_id: str, session: SessionDep):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return [
        UserAchievementResponse(**achievement.model_dump(), unlocked=True)
        for achievement in user.achievements
    ]


@router.get("/user/{user_id}/{achievement_id}", response_model=UserAchievementResponse)
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
    "/user/{user_id}/unlock/{achievement_id}", response_model=UserAchievementResponse
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


@router.post("/admin/create", response_model=AchievementResponse)
def admin_create_achievement(
    achievement: AchievementRequest,
    session: SessionDep,
    auth_result: str = Security(auth.verify, scopes=["TODO:admin_scope_or_something"]),
):
    saved_achievement = Achievement.model_validate(
        Achievement(**achievement, unlocked_by=[])
    )
    session.add(saved_achievement)
    session.commit()
    session.refresh(saved_achievement)
    return AchievementResponse(**achievement.model_dump())
