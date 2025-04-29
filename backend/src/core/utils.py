from fastapi import HTTPException, status

from core.config import settings


def validate_user_id(auth_user_id: str, claimed_user_id: str):
    """Check if declared user id matches token. If not, raise 403."""

    if settings.skip_auth:
        return

    if auth_user_id.strip() != claimed_user_id.strip():
        raise HTTPException(status.HTTP_403_FORBIDDEN)
