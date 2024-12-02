from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from enum import Enum

class TrashType(str, Enum):
    paper = "paper"
    plastic = "plastic"
    glass = "glass"
    other = "other"

class ItemOrder(str, Enum):
    id = "id"


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


@app.get("/api/v1/item/{item_id}")
async def get_item(item_id: int):
    pass