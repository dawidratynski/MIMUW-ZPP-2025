from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from sqlmodel import Session

from data_enums import TrashType, ItemOrder
from db import engine, create_db_and_tables, get_session
from models import Item



SessionDep = Annotated[Session, Depends(get_session)]

create_db_and_tables()
app = FastAPI()



# Directory for storing public static files
# Photos are stored in /static/photos
app.mount("/static", StaticFiles(directory="static"), name="static")



@app.get("/")
async def root():
    pass



@app.get("/api/v1/item/search")
async def search_items(
    types: Annotated[list[TrashType] | None, Query()] = None,
    collected: bool | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    order_by: ItemOrder = ItemOrder.id,
    lat_min: Annotated[int, Query(ge=-90, le=90)] = -90,
    lat_max: Annotated[int, Query(ge=-90, le=90)] = 90,
    lon_min: Annotated[int, Query(ge=-180, le=180)] = -180,
    lon_max: Annotated[int, Query(ge=-180, le=180)] = 180,
    count: int = 50,
    
    # TODO:
    # nowrap_lon
    # time_min
    # time_max
    # submitted_by: 
    # # Tolerance used to determine results (in degrees)
    # location_tolerance: float = 0.000001,  # Default: <= 11 cm
):
    pass



@app.post("/api/v1/item/submit")
async def get_item(item: Item, session: SessionDep):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item



@app.get("/api/v1/item/{item_id}")
async def get_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Hero not found")
    return item
