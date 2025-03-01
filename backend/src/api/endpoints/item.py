from datetime import datetime
from typing import Annotated, List
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, Form, HTTPException, Query, Security
from pydantic import TypeAdapter
from pydantic_core import ValidationError
from sqlmodel import select

from core.auth import VerifyToken
from core.db import SessionDep
from core.models.item import (
    BoundingBox,
    BoundingBoxRequest,
    Item,
    ItemCreate,
    ItemResponse,
)

auth = VerifyToken()

router = APIRouter(prefix="/item")


async def _validate_item_submission(
    item: ItemCreate, bounding_boxes: list[BoundingBoxRequest]
):
    """Checks if the item and photo are a valid submission"""
    # TODO: Check if file is a photo (maybe using PIL?)
    # TODO: Check if file name is valid
    # TODO: Check if file extension is acceptable and matches detected by PIL
    # TODO: Check if file is acceptable size
    # TODO: Check if all bounding box coords are within the photo
    pass


async def _validate_and_save_submission(
    item: ItemCreate, bounding_boxes: list[BoundingBoxRequest]
) -> str:
    """Validates the photo and item. If needed, resizes the photo and
    bounding boxes. Returns photo id."""

    await _validate_item_submission(item, bounding_boxes)

    photo_id = uuid4().hex
    photo_ext = item.photo.filename.split(".")[-1]
    photo_filename = photo_id + "." + photo_ext

    # Use async file io to not block main event loop
    async with aiofiles.open(f"/{photo_filename}", "wb+") as f:
        while photo_chunk := await item.photo.read(1024):
            await f.write(photo_chunk)

    return photo_id


@router.post("/submit", response_model=ItemResponse)
async def create_item(
    item: Annotated[ItemCreate, Form(media_type="multipart/form-data")],
    session: SessionDep,
    auth_result: str = Security(auth.verify),
):
    try:
        bounding_boxes = [
            BoundingBox.from_request(bb)
            for bb in TypeAdapter(List[BoundingBoxRequest]).validate_json(
                item.bounding_boxes_json
            )
        ]
    except ValidationError:
        raise HTTPException(status_code=400, detail="Provided bounding boxes JSON is invalid")

    photo_id = await _validate_and_save_submission(item, bounding_boxes)

    item = Item(
        **item.model_dump(),
        photo_id=photo_id,
        uploaded_at=datetime.now(),
        bounding_boxes=bounding_boxes,
    )

    saved_item = Item.model_validate(item)
    session.add(saved_item)
    session.commit()
    session.refresh(saved_item)
    return saved_item.into_response()


@router.get("/list", response_model=list[ItemResponse])
def list_items(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=50)] = 50,
):
    items = session.exec(select(Item).offset(offset).limit(limit)).all()
    return [item.into_response() for item in items]


# TODO - Complete rework
@router.get("/search", response_model=list[ItemResponse])
def search_items(
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

    return [item.into_response() for item in items]


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="No item with given id found")

    return item.into_response()
