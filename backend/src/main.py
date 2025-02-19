from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import api
from core.config import settings
from core.db import setup_db

setup_db()

app = FastAPI(title=settings.project_name)

allow_cors_origins = [str(origin) for origin in settings.backend_cors_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)
