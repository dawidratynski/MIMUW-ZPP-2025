from fastapi import APIRouter

from api.endpoints import achievement, item, user
from core.auth import VerifyToken

auth = VerifyToken()


router = APIRouter(prefix="/api/v1")

router.include_router(item.router)
router.include_router(achievement.router)
router.include_router(user.router)

# Example endpoints with properly working auth:
#
# from api.endpoints import auth_example
# router.include_router(auth_example.router)
