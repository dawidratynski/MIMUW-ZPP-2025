from datetime import datetime
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Security
from sqlmodel import select

from core.auth import VerifyToken
from core.db import SessionDep
from core.models.item import Item, ItemCreate, ItemResponse

auth = VerifyToken()

router = APIRouter(prefix="/item")


# TODO: Add photo upload
@router.post("/submit", response_model=ItemResponse)
async def create_item(
    item: ItemCreate, session: SessionDep, auth_result: str = Security(auth.verify)
):
    item = Item(
        id=None,
        photo_id=uuid4().hex,
        uploaded_at=datetime.now(),
        bounding_boxes=[],  # TODO - Insert bounding boxes to db
        **item.model_dump(),
    )
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item.into_response_model()


@router.get("/list", response_model=list[ItemResponse])
async def list_items(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=50)] = 50,
):
    items = session.exec(select(Item).offset(offset).limit(limit)).all()
    return [item.into_response_model() for item in items]


# TODO - Complete rework
@router.get("/search", response_model=list[ItemResponse])
async def search_items(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=50)] = 50,
    lat_min: Annotated[float, Query(ge=-90, le=90)] = -90,
    lat_max: Annotated[float, Query(ge=-90, le=90)] = 90,
    lon_min: Annotated[float, Query(ge=-180, le=180)] = -180,
    lon_max: Annotated[float, Query(ge=-180, le=180)] = 180,
):
    items = session.exec(
        select(Item)
        .filter(Item.latitude >= lat_min)
        .filter(Item.latitude <= lat_max)
        # TODO: Handle wraparounds
        .filter(Item.longitude >= lon_min)
        .filter(Item.longitude <= lon_max)
        .offset(offset)
        .limit(limit)
    ).all()

    return [item.into_response_model() for item in items]


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="No item with given id found")

    return item.into_response_model()
