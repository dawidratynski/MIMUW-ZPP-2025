from fastapi import APIRouter, HTTPException, Security
from sqlmodel import select

from core.auth import VerifyToken
from core.db import SessionDep
from core.models.achievement import (
    Achievement,
    AchievementRequest,
    AchievementResponse,
)

auth = VerifyToken()

router = APIRouter(prefix="/achievements")


@router.get("/", response_model=list[AchievementResponse])
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


@router.post("/", response_model=AchievementResponse)
def create_achievement(
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
