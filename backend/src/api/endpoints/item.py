from datetime import datetime
from pathlib import Path
from typing import Annotated, List
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, Form, HTTPException, Query, Security
from geoalchemy2 import WKTElement
from geoalchemy2 import functions as geofunc
from pydantic import TypeAdapter
from pydantic_core import ValidationError
from sqlmodel import or_, select

from core.auth import VerifyToken
from core.db import SessionDep
from core.models.item import (
    BoundingBox,
    BoundingBoxRequest,
    Item,
    ItemCreate,
    ItemResponse,
    ItemType,
)
from core.utils import validate_user_id

auth = VerifyToken()

router = APIRouter(prefix="/item")


async def _validate_item_submission(
    item: ItemCreate, bounding_boxes: list[BoundingBoxRequest]
):
    """Checks if the item and image are a valid submission"""
    # TODO: Check if file is an image (maybe using PIL?)
    # TODO: Check if file name is valid
    # TODO: Check if file extension is acceptable and matches detected by PIL
    # TODO: Check if file is acceptable size
    # TODO: Check if all bounding box coords are within the image
    pass


async def _validate_and_save_submission(
    item: ItemCreate, bounding_boxes: list[BoundingBoxRequest]
) -> str:
    """Validates the image and item. Returns path where the image was saved."""

    await _validate_item_submission(item, bounding_boxes)

    image_ext = item.image.filename.split(".")[-1].lower()

    image_path = Path("/image") / f"{uuid4().hex}.{image_ext}"

    # Use async file io to not block main event loop
    async with aiofiles.open(image_path, "wb+") as f:
        while image_chunk := await item.image.read(1024 * 1024):  # 1 MB
            await f.write(image_chunk)

    return image_path.as_posix()


def _extract_bounding_boxes(item: ItemCreate) -> list[BoundingBoxRequest]:
    try:
        return [
            BoundingBox.from_request(bb)
            for bb in TypeAdapter(List[BoundingBoxRequest]).validate_json(
                item.bounding_boxes_json
            )
        ]
    except ValidationError:
        raise HTTPException(
            status_code=400, detail="Provided bounding boxes JSON is invalid"
        )


@router.post("/submit", response_model=ItemResponse)
async def create_item(
    item: Annotated[ItemCreate, Form(media_type="multipart/form-data")],
    session: SessionDep,
    auth_result: str = Security(auth.verify),
):
    validate_user_id(auth_result, item.user_id)

    bounding_boxes = _extract_bounding_boxes(item)
    image_path = await _validate_and_save_submission(item, bounding_boxes)

    item = Item(
        **item.model_dump(),
        location=WKTElement(f"POINT({item.longitude} {item.latitude})", srid=4326),
        image_path=image_path,
        uploaded_at=datetime.now(),
        bounding_boxes=bounding_boxes,
    )

    saved_item = Item.model_validate(item)
    session.add(saved_item)
    session.commit()
    session.refresh(saved_item)
    return saved_item.into_response()


@router.get("/search", response_model=list[ItemResponse])
def search_items(  # noqa: C901
    # fmt: off
    session: SessionDep,

    offset: int = Query(ge=0, default=0),
    limit: int = Query(le=1000, default=100),

    author_id: str | None = None,

    created_before: datetime | None = None,
    created_after: datetime | None = None,

    uploaded_before: datetime | None = None,
    uploaded_after: datetime | None = None,

    latitude_min: float | None = Query(ge=-90, le=90, default=None),
    latitude_max: float | None = Query(ge=-90, le=90, default=None),

    longitude_min: float | None = Query(ge=-180, le=180, default=None),
    longitude_max: float | None = Query(ge=-180, le=180, default=None),

    nearby_center_latitude: float | None = Query(ge=-90, le=90, default=None),
    nearby_center_longitude: float | None = Query(ge=-180, le=180, default=None),
    nearby_radius_meters: float | None = None,

    contains_item_type: ItemType | None = None,
    # fmt: on
):
    query = select(Item)

    if author_id:
        query = query.where(Item.user_id == author_id)

    if created_before:
        query = query.where(Item.created_at < created_before)
    if created_after:
        query = query.where(Item.created_at > created_after)

    if uploaded_before:
        query = query.where(Item.uploaded_at < uploaded_before)
    if uploaded_after:
        query = query.where(Item.uploaded_at > uploaded_after)

    if latitude_min is not None:
        query = query.where(Item.latitude >= latitude_min)
    if latitude_max is not None:
        query = query.where(Item.latitude <= latitude_max)

    if (
        longitude_min is not None
        and longitude_max is not None
        and longitude_min > longitude_max
    ):
        # Special case: Longitude range crosses 180/-180 line
        query = query.where(
            or_(Item.longitude >= longitude_min, Item.longitude <= longitude_max)
        )

    else:
        if longitude_min is not None:
            query = query.where(Item.longitude >= longitude_min)
        if longitude_max is not None:
            query = query.where(Item.longitude <= longitude_max)

    if (
        nearby_center_latitude is not None
        and nearby_center_longitude is not None
        and nearby_radius_meters is not None
    ):
        center_point = (
            f"SRID=4326;POINT({nearby_center_longitude} {nearby_center_latitude})"
        )

        query = query.where(
            geofunc.ST_DWithin(Item.location, center_point, nearby_radius_meters)
        )

    if contains_item_type:
        query = (
            query.join(BoundingBox, BoundingBox.item_id == Item.id)
            .where(BoundingBox.item_type == contains_item_type)
            .distinct()
        )

    items = session.exec(query.offset(offset).limit(limit)).all()

    return [item.into_response() for item in items]


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="No item with given id found")

    return item.into_response()


@router.post("/{item_id}/collect", response_model=ItemResponse)
def mark_as_collected(
    session: SessionDep,
    item_id: int,
    user_id: str,
    auth_result: str = Security(auth.verify),
):
    validate_user_id(auth_result, user_id)

    item = session.get(Item, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="No item with given id found")

    if item.collected:
        raise HTTPException(status_code=400, detail="Item is already collected")

    item.collected = True
    item.collected_by = user_id
    item.collected_timestamp = datetime.now()

    session.commit()
    session.refresh(item)

    return item.into_response()
