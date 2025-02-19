from fastapi import APIRouter, Security

from core.auth import VerifyToken

auth = VerifyToken()


router = APIRouter(prefix="/api/v1")


@router.get("/")
def home():
    return "Hello, World!"


@router.get("/public")
def public():
    """No access token required to access this route"""

    result = {
        "status": "success",
        "msg": (
            "Hello from a public endpoint! You don't need to be "
            "authenticated to see this."
        ),
    }
    return result


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
