"""Reviewed local photographs by stable food ID, with licensed fallbacks."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METADATA = json.loads((ROOT / "assets/foods/metadata.json").read_text())
try:
    PHOTOS = json.loads((ROOT / "assets/foods/photos/metadata.json").read_text())
except (OSError, ValueError):
    PHOTOS = {"photos": {}, "food_mappings": {}}


def _local_paths(metadata: dict) -> dict:
    path = ROOT / metadata["path"]
    thumbnail = ROOT / metadata.get("thumbnail_path", metadata["path"])
    return {**metadata, "absolute_path": str(path), "thumbnail_absolute_path": str(thumbnail if thumbnail.is_file() else path)}


def image_metadata(food: dict) -> dict:
    # Generic photographs never substitute for an exact branded product image.
    if food["data_type"] != "Branded":
        photo_key = PHOTOS.get("food_mappings", {}).get(food["food_id"])
        photo = PHOTOS.get("photos", {}).get(photo_key)
        if photo and (ROOT / photo.get("path", "missing")).is_file():
            return _local_paths({**photo, "key": photo_key})
    if food["data_type"] == "Branded":
        key = "product-placeholder"
    else:
        text = food["description"].casefold()
        terms = {"tofu": "tofu", "edamame": "edamame", "yogurt": "yogurt", "spinach": "spinach", "broccoli": "broccoli", "carrot": "carrot", "tomato": "tomato", "apples": "apple", "bananas": "banana", "avocado": "avocado", "egg,": "egg", "milk,": "milk", "oil,": "oil", "sweet potato": "sweet-potato", "lentils": "beans", "chickpeas": "beans", "beans,": "beans", "rice": "grains", "oats": "grains", "quinoa": "grains"}
        key = next((value for term, value in terms.items() if term in text), "product-placeholder")
    metadata = METADATA.get(key, METADATA["product-placeholder"])
    if not (ROOT / metadata["path"]).is_file():
        metadata = METADATA["product-placeholder"]
        key = "product-placeholder"
    return _local_paths({**metadata, "key": key, "kind": "illustration", "review_note": "Photo unavailable. Original representative illustration, not an exact food or product photograph."})
