from enum import Enum


class TrashType(str, Enum):
    paper = "paper"
    plastic = "plastic"
    glass = "glass"
    other = "other"


class ItemOrder(str, Enum):
    id = "id"
