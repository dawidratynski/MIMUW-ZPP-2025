from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from sqlmodel import Session, select

from data_enums import TrashType
from db import engine, create_db_and_tables, get_session
from models import Item, ItemCreate, ItemPublic



SessionDep = Annotated[Session, Depends(get_session)]

create_db_and_tables()
app = FastAPI()



# Directory for storing public static files
# Photos are stored in /static/photos
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/web", StaticFiles(directory="frontend", html=True), name="frontend")


@app.post("/api/v1/item/submit", response_model=ItemPublic)
async def create_item(item: ItemCreate, session: SessionDep):
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@app.get("/api/v1/item/list", response_model=list[ItemPublic])
async def list_items(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=50)] = 50,
):
    items = session.exec(
        select(Item)
        .offset(offset)
        .limit(limit)
    ).all()
    return items


@app.get("/api/v1/item/search", response_model=list[ItemPublic])
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


@app.get("/api/v1/item/{item_id}", response_model=ItemPublic)
async def get_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="No such item")
    return item
