from fastapi import APIRouter

from api.endpoints import auth_example, item
from core.auth import VerifyToken

auth = VerifyToken()


router = APIRouter(prefix="/api/v1")

router.include_router(item.router)
router.include_router(auth_example.router)


@router.get("/")
def hello_world():
    return "Hello, World!"
