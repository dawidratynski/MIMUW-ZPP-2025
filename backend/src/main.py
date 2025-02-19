from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware

from utils.auth import VerifyToken

app = FastAPI()
auth = VerifyToken()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return "Hello, World!"

@app.get("/api/public")
def public():
    """No access token required to access this route"""

    result = {
        "status": "success",
        "msg": ("Hello from a public endpoint! You don't need to be "
                "authenticated to see this.")
    }
    return result

@app.get("/api/private")
def private(auth_result: str = Security(auth.verify)):
    """A valid access token is required to access this route"""
    return auth_result


@app.get("/api/private-scoped")
def private_scoped(auth_result: str = Security(auth.verify, scopes=['dev:test_scope'])):
    """A valid access token and an appropriate scope are required to access
    this route
    """

    return auth_result