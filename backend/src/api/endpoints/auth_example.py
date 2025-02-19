from fastapi import APIRouter, Security

from core.auth import VerifyToken

auth = VerifyToken()

router = APIRouter(prefix="/auth_example")


@router.get("/public")
def public():
    """No access token required to access this route"""

    return {"status": "success", "msg": "This should work without auth"}


@router.get("/private")
def private(auth_result: str = Security(auth.verify)):
    """A valid access token is required to access this route"""
    return auth_result


@router.get("/private-scoped")
def private_scoped(auth_result: str = Security(auth.verify, scopes=["dev:test_scope"])):
    """A valid access token and an appropriate scope are required to access
    this route
    """
    return auth_result
