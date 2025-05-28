from fastapi import HTTPException
from PIL import Image

import core.detection
import core.detection.rtdetr
import core.detection.yolo
from core.config import settings
from core.models.item import BoundingBoxResponse


def get_bounding_boxes(image: Image.Image) -> list[BoundingBoxResponse]:
    match settings.detection_model:
        case "YOLO":
            return core.detection.yolo.get_bounding_boxes(image)
        case "RTDETR":
            return core.detection.rtdetr.get_bounding_boxes(image)
        case _:
            raise HTTPException(
                500, "Invalid model configuration. Please notify the administrator."
            )
