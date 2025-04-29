from fastapi import APIRouter

from api.endpoints import achievement, item, user
from core.auth import VerifyUserID

auth = VerifyUserID()


router = APIRouter(prefix="/api/v1")

router.include_router(item.router)
router.include_router(achievement.router)
router.include_router(user.router)
