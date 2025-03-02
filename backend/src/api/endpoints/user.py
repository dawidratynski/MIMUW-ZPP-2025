from fastapi import APIRouter, Security

from core.auth import VerifyToken
from core.db import SessionDep
from core.models.user import User, UserResponse
from core.utils import validate_user_id

auth = VerifyToken()

router = APIRouter(prefix="/user")


@router.get("/register", response_model=UserResponse)
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
