from sqlmodel import Session, create_engine, SQLModel
import os

POSTGRES_USER = os.getenv("POSTGRES_USER", "zpp")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "zpp")
POSTGRES_DB = os.getenv("POSTGRES_DB", "zpp")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")


DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(bind=engine)

def get_session():
    with Session(engine) as session:
        yield session
        