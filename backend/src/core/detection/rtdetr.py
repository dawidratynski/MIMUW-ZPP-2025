import io
from typing import Dict

import numpy as np
import torch
from google import genai
from google.genai import types
from PIL import Image
from transformers import RTDetrForObjectDetection, RTDetrImageProcessor  # type:ignore

from core.config import settings
from core.models.item import BoundingBoxResponse, ItemType

client = genai.Client(api_key=settings.gemini_api_key)
model_path_rt_detr = "/backend/src/core/detection/models/rtdetr.pt"


def get_checkpoint_rt_detr():
    return "PekingU/rtdetr_r50vd_coco_o365"


def load_model_rt_detr(model_path):
    checkpoint = get_checkpoint_rt_detr()
    rtdetr_model = RTDetrForObjectDetection.from_pretrained(
        checkpoint,
        id2label={0: "Paper", 1: "Glass", 2: "Metal", 3: "Plastic", 4: "Other"},
        label2id={"Paper": 0, "Glass": 1, "Metal": 2, "Plastic": 3, "Other": 4},
        num_labels=5,
        ignore_mismatched_sizes=True,
    )
    model_dict = torch.load(model_path, map_location="cpu", weights_only=True)
    rtdetr_model.load_state_dict(model_dict["model_state_dict"])
    rtdetr_model.eval()
    return rtdetr_model


rtdetr_model = load_model_rt_detr(model_path_rt_detr)


def process_image_rt_detr(image: Image.Image) -> Dict[str, torch.Tensor]:
    checkpoint = get_checkpoint_rt_detr()
    image_processor = RTDetrImageProcessor.from_pretrained(checkpoint)
    rtdetr_model = load_model_rt_detr(model_path_rt_detr)

    threshold = 0.6

    inputs = image_processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = rtdetr_model(**inputs)

    results = image_processor.post_process_object_detection(
        outputs=outputs,
        threshold=threshold,
        target_sizes=torch.tensor([image.size[::-1]]),
    )[0]

    results_size = len(results["labels"])
    boxes = torch.zeros((results_size, 4), dtype=torch.float32)
    labels = torch.zeros((results_size,), dtype=torch.int64)
    scores = torch.zeros((results_size,), dtype=torch.float32)

    for idx, (score, label, box) in enumerate(
        zip(results["scores"], results["labels"], results["boxes"])
    ):
        cls_id = get_class_number_rt_detr(rtdetr_model.config.id2label[label.item()])
        if cls_id == -1:
            continue

        boxes[idx] = torch.tensor([int(i) for i in box.tolist()])
        labels[idx] = cls_id
        scores[idx] = round(score.item(), 3)

    return {"boxes": boxes, "labels": labels, "scores": scores}


def get_class_number_rt_detr(name):
    if "Paper" in name:
        return 0
    if "Glass" in name:
        return 1
    if "Metal" in name:
        return 2
    if "Plastic" in name:
        return 3
    return -1


def get_boxes_and_labels_rt_detr(image: Image.Image):
    results = process_image_rt_detr(image)
    boxes = results["boxes"]
    original_labels = results["labels"]

    final_labels = []

    for i, box in enumerate(boxes):
        try:
            xmin, ymin, xmax, ymax = box.tolist()
            cropped_image = image.crop((xmin, ymin, xmax, ymax))
            buffer = io.BytesIO()
            cropped_image.save(buffer, format="JPEG")
            image_bytes = buffer.getvalue()
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-04-17",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    "What type of trash is in the picture? Choose between: Paper, Plastic, Metal, Glass. Respond using only one word.",  # noqa:E501
                ],
            )

            label = get_class_number_rt_detr(response.text)
            if label == -1:
                final_labels.append(
                    original_labels[i].item()
                    if isinstance(original_labels[i], torch.Tensor)
                    else original_labels[i]
                )
            else:
                final_labels.append(label)
        except Exception:
            final_labels.append(
                original_labels[i].item()
                if isinstance(original_labels[i], torch.Tensor)
                else original_labels[i]
            )

    return {
        "boxes": boxes,  # torch tensor  [xmin, ymin, xmax, ymax]
        "labels": final_labels,  # list
    }


def get_bounding_boxes(image: Image.Image) -> list[BoundingBoxResponse]:
    results = get_boxes_and_labels_rt_detr(image)
    bounding_boxes = []

    model_label_to_item_type = {
        0: ItemType.paper,
        1: ItemType.glass,
        2: ItemType.metal,
        3: ItemType.plastic,
    }

    boxes = results["boxes"]  # torch.Tensor of shape (N, 4)
    labels = results["labels"]

    for i in range(boxes.shape[0]):
        box = boxes[i]
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
