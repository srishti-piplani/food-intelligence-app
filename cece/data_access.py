"""Validated local USDA records; no runtime network access."""

import hashlib
import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
NUTRIENTS = {
    "calories_kcal": (1008, "kcal", 1000),
    "protein_g": (1003, "g", 100),
    "carbohydrates_g": (1005, "g", 100),
    "fat_g": (1004, "g", 100),
    "fiber_g": (1079, "g", 100),
}
DETAIL_NUTRIENTS = {
    "total_sugars_g": (2000, "g", 100),
    "added_sugars_g": (1235, "g", 100),
    "saturated_fat_g": (1258, "g", 100),
    "trans_fat_g": (1257, "g", 100),
    "sodium_mg": (1093, "mg", 100000),
    "cholesterol_mg": (1253, "mg", 100000),
}
ALL_NUTRIENTS = {**NUTRIENTS, **DETAIL_NUTRIENTS}
REQUIRED = {
    "food_id", "description", "brand", "fdc_id", "data_type", "basis_g",
    "source_url", "source_archive", "raw_record", "raw_sha256",
    *ALL_NUTRIENTS, *(f"{name}_missing" for name in ALL_NUTRIENTS),
}


def normalize_record(record: dict, source_archive: str) -> dict:
    """Use published foodNutrients, already standardized by USDA; never labelNutrients."""
    kind = record["dataType"]
    if kind not in {"SR Legacy", "Branded"}:
        raise ValueError(f"Unsupported basis/data type: {kind}")
    if kind == "Branded" and str(record.get("servingSizeUnit", "")).lower() not in {"g", "grm"}:
        raise ValueError("Branded volume basis cannot be treated as 100 g")
    fdc_id = record["fdcId"]
    result = {
        "food_id": f"usda-{fdc_id}", "description": record["description"],
        "brand": record.get("brandName") or record.get("brandOwner") or "",
        "fdc_id": fdc_id, "data_type": kind, "basis_g": 100,
        "source_url": f"https://fdc.nal.usda.gov/food-details/{fdc_id}/nutrients",
        "source_archive": source_archive, "raw_record": f"raw/{fdc_id}.json",
    }
    for name, (nutrient_id, unit, _) in ALL_NUTRIENTS.items():
        matches = [n for n in record["foodNutrients"] if n["nutrient"]["id"] == nutrient_id]
        if len(matches) > 1:
            raise ValueError(f"Ambiguous nutrient {nutrient_id}")
        if matches and matches[0]["nutrient"]["unitName"].lower() != unit:
            raise ValueError(f"Unexpected unit for {name}")
        amount = matches[0].get("amount") if matches else None
        result[name] = amount
        result[f"{name}_missing"] = amount is None
    return result


def validate_foods(frame: pd.DataFrame) -> None:
    """Reject malformed data rather than repairing it silently."""
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Empty dataset")
    for column in ("food_id", "fdc_id"):
        if frame[column].isna().any() or frame[column].duplicated().any():
            raise ValueError(f"Missing or duplicate {column}")
    ids = pd.to_numeric(frame.fdc_id, errors="coerce")
    if ids.isna().any() or (ids <= 0).any() or (ids % 1 != 0).any():
        raise ValueError("Invalid USDA identifier")
    if not frame.food_id.eq(ids.map(lambda value: f"usda-{int(value)}")).all():
        raise ValueError("Food identifier mismatch")
    if not frame.basis_g.eq(100).all() or not frame.data_type.isin(["SR Legacy", "Branded"]).all():
        raise ValueError("Invalid nutrient basis or data type")
    for column in ("description", "source_url", "source_archive", "raw_record", "raw_sha256"):
        if frame[column].isna().any() or frame[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Missing provenance: {column}")
    for name, (_, _, maximum) in ALL_NUTRIENTS.items():
        values = pd.to_numeric(frame[name], errors="coerce")
        if (values.isna() & frame[name].notna()).any():
            raise ValueError(f"Non-numeric {name}")
        if ((values < 0) | (values > maximum)).any():
            raise ValueError(f"Out-of-range {name}")
        flags = frame[f"{name}_missing"]
        if not flags.map(lambda v: isinstance(v, bool)).all() or not flags.eq(values.isna()).all():
            raise ValueError(f"Incorrect missing indicator: {name}")


def load_foods(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """Validate schema, record count, and file integrity before returning data."""
    path = data_dir / "foods.csv"
    manifest = json.loads((data_dir / "manifest.json").read_text())
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["sha256"]:
        raise ValueError("Dataset checksum mismatch")
    frame = pd.read_csv(path, keep_default_na=True)
    validate_foods(frame)
    if len(frame) != manifest["record_count"]:
        raise ValueError("Manifest record count mismatch")
    return frame


def search_foods(frame: pd.DataFrame, query: str) -> pd.DataFrame:
    """Match every whitespace-separated term literally across name and brand.

    Word order is flexible (e.g. 'cooked lentils'). Empty input browses all foods.
    """
    text = frame.description.fillna("").str.casefold() + " " + frame.brand.fillna("").str.casefold()
    matches = pd.Series(True, index=frame.index)
    for term in query.casefold().split():
        matches &= text.str.contains(term, regex=False)
    return frame.loc[matches].copy()
