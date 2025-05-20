import io

import numpy as np
import torch
from google import genai
from google.genai import types
from PIL import Image
from ultralytics import YOLO  # type: ignore
from ultralytics.engine.results import Results  # type: ignore

from core.config import settings
from core.models.item import BoundingBoxResponse, ItemType

model_path = "/backend/src/core/detection/detectionModel.pt"
model = YOLO(model_path)
client = genai.Client(api_key=settings.gemini_api_key)


def _compute_intersection_over_union(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area if union_area != 0 else 0


# applies NMS to boxes
def _nms_no_class(boxes, scores, iou_threshold=0.95):
    indices = scores.argsort(descending=True)
    keep = []

    while indices.numel() > 0:
        current = indices[0]
        keep.append(current.item())
        if indices.numel() == 1:
            break

        current_box = boxes[current]
        rest_boxes = boxes[indices[1:]]

        ious = torch.tensor(
            [_compute_intersection_over_union(current_box, box) for box in rest_boxes]
        )
        indices = indices[1:][ious <= iou_threshold]

    return keep


def _get_class_number(name):
    if "Paper" in name:
        return 0
    if "Glass" in name:
        return 1
    if "Metal" in name:
        return 2
    if "Plastic" in name:
        return 3
    return -1


# asks gemini for label and returns it
def _get_label(result, box, fallback_label):
    try:
        x1 = int(np.floor(box[0]))
        y1 = int(np.floor(box[1]))
        x2 = int(np.ceil(box[2]))
        y2 = int(np.ceil(box[3]))
        image = result.orig_img[y1:y2, x1:x2]
        pil_image = Image.fromarray(image.astype(np.uint8), mode="RGB")
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()
        response = client.models.generate_content(
            model="gemini-2.5-pro-preview-05-06",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                "What type of trash is in the picture. Choose between: Paper, Plastic, Metal, Glass. Respond using only one word.",  # noqa:E501
            ],
        )
        label = _get_class_number(response.text)
        if label == -1:
            return fallback_label
        return label

    except Exception:
        return fallback_label


def _get_boxes_and_labels(image: Image.Image) -> list[Results]:
    results: list[Results] = model(image)
    for result in results:
        boxes = result.boxes.xyxy
        scores = result.boxes.conf

        if boxes.nelement() == 0:
            continue

        keep_indices = _nms_no_class(boxes, scores, iou_threshold=0.95)
        keep_indices_tensor = torch.tensor(keep_indices, dtype=torch.long)

        result.boxes.data = result.boxes.data[keep_indices_tensor]

        new_labels = []
        for i, box in enumerate(result.boxes.xyxy):
            fallback = int(result.boxes.cls[i].item())
            label = _get_label(result, box, fallback)
            new_labels.append(label)

        result.boxes.data[:, -1] = torch.tensor(new_labels, dtype=torch.float32)
    return results


def get_bounding_boxes(image: Image.Image) -> list[BoundingBoxResponse]:
    results = _get_boxes_and_labels(image)
    bounding_boxes = []

    model_label_to_item_type = {
        0: ItemType.paper,
        1: ItemType.glass,
        2: ItemType.metal,
        3: ItemType.plastic,
    }

    for result in results:
        boxes = result.boxes.xyxy
        labels = result.boxes.data[:, -1].int().tolist()

        for i, box in enumerate(boxes):
            label = labels[i]
            item_type = model_label_to_item_type.get(label, ItemType.unknown)

            x_left = int(np.floor(box[0].item()))
            y_top = int(np.floor(box[1].item()))
            x_right = int(np.ceil(box[2].item()))
            y_bottom = int(np.ceil(box[3].item()))

            bounding_box = BoundingBoxResponse(
                item_type=item_type,
                x_left=x_left,
                x_right=x_right,
                y_top=y_top,
                y_bottom=y_bottom,
            )

            bounding_boxes.append(bounding_box)

    return bounding_boxes
