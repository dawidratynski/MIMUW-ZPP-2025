from fastapi import HTTPException, status


def validate_user_id(auth_result: str, user_id: str):
    """Check if declared user id matches token. If not, raise 403."""
    is_valid = True  # TODO

    if not is_valid:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "User id doesn't match authorization token"
        )
