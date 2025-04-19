from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import api
from core.config import settings
from core.db import setup_db

setup_db()

app = FastAPI(title=settings.project_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path("/image").mkdir(parents=True, exist_ok=True)
app.mount("/image", StaticFiles(directory="/image"), name="image")

app.include_router(api.router)
