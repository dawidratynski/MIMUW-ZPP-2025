from fastapi import APIRouter, Security

from core.auth import VerifyToken
from core.db import SessionDep
from core.models.user import User, UserResponse

auth = VerifyToken()

router = APIRouter(prefix="/user")


@router.get("/register", response_model=UserResponse)
def register_user(
    user_id: str,
    session: SessionDep,
    auth_result: str = Security(auth.verify),
):
    """
    Register user in database if not already present
    """

    # TODO: Check if user_id matches auth_result OR get user_id from auth_result

    if session.get(User, user_id):
        return

    user = User(id=user_id, achievements=[])
    saved_user = User.model_validate(user)
    session.add(saved_user)
    session.commit()
    session.refresh(saved_user)
    return saved_user.into_response()
