from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Security
from sqlmodel import select

from core.auth import VerifyToken
from core.db import SessionDep
from core.models.enums import TrashType
from core.models.item import Item, ItemCreate, ItemPublic

auth = VerifyToken()

router = APIRouter(prefix="/item")


@router.get("/")
def home():
    return "Hello, World!"


@router.post("/submit", response_model=ItemPublic)
async def create_item(
    item: ItemCreate, session: SessionDep, auth_result: str = Security(auth.verify)
):
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get("/list", response_model=list[ItemPublic])
async def list_items(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=50)] = 50,
):
    items = session.exec(select(Item).offset(offset).limit(limit)).all()
    return items


@router.get("/search", response_model=list[ItemPublic])
async def search_items(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=50)] = 50,
    item_type: Annotated[TrashType | None, Query()] = None,
    lat_min: Annotated[float, Query(ge=-90, le=90)] = -90,
    lat_max: Annotated[float, Query(ge=-90, le=90)] = 90,
    lon_min: Annotated[float, Query(ge=-180, le=180)] = -180,
    lon_max: Annotated[float, Query(ge=-180, le=180)] = 180,
):
    return session.exec(
        select(Item)
        .filter((item_type is None) or (Item.type == item_type))
        .filter(Item.latitude >= lat_min)
        .filter(Item.latitude <= lat_max)
        # TODO: Handle wraparounds
        .filter(Item.longitude >= lon_min)
        .filter(Item.longitude <= lon_max)
        .offset(offset)
        .limit(limit)
    ).all()


@router.get("/{item_id}", response_model=ItemPublic)
async def get_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="No such item")
    return item
