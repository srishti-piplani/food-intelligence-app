"""Pure gram-based portion scaling; missing nutrients stay missing."""

import math
from numbers import Real

from cece.data_access import ALL_NUTRIENTS


def calculate_portion(food: dict, grams: float) -> dict:
    """Scale a validated per-100-g record to a nonnegative gram portion."""
    if isinstance(grams, bool) or not isinstance(grams, Real) or not math.isfinite(grams) or grams < 0:
        raise ValueError("Portion must be a finite, nonnegative number of grams")
    if food.get("basis_g") != 100:
        raise ValueError("Expected a per-100-g food record")
    result = {"portion_g": grams}
    for name in ALL_NUTRIENTS:
        value = food[name]
        missing = value is None or (isinstance(value, Real) and math.isnan(value))
        if not missing and (not isinstance(value, Real) or not math.isfinite(value) or value < 0):
            raise ValueError(f"Invalid nutrient: {name}")
        result[name] = None if missing else value * grams / 100
        result[f"{name}_missing"] = missing
    return result


def protein_per_100_kcal(food: dict) -> float | None:
    """Protein density from the 100-g basis; missing/zero energy is undefined."""
    calories, protein = food["calories_kcal"], food["protein_g"]
    if any(isinstance(v, bool) or not isinstance(v, Real) or not math.isfinite(v) for v in (calories, protein)):
        return None
    if calories <= 0 or protein < 0:
        return None
    return protein * 100 / calories


def comparison_insights(rows: list[dict]) -> list[dict]:
    """Rank known finite values only; preserve all ties (float tolerance 1e-9)."""
    observations = []
    for field, title, minimum, unit in (
        ("protein_g", "Highest protein", False, "g"),
        ("fiber_g", "Highest fiber", False, "g"),
        ("calories_kcal", "Lowest calories", True, "kcal"),
        ("protein_density", "Highest protein per 100 kcal", False, "g / 100 kcal"),
    ):
        known = [r for r in rows if isinstance(r.get(field), Real) and not isinstance(r[field], bool) and math.isfinite(r[field]) and r[field] >= 0]
        value = (min if minimum else max)([r[field] for r in known]) if known else None
        observations.append({"title": title, "unit": unit, "value": value,
                             "foods": [r["Food"] for r in known if math.isclose(r[field], value, rel_tol=1e-9, abs_tol=1e-9)],
                             "known_count": len(known), "total_count": len(rows)})
    return observations


def comparison_snapshot(foods: list[dict], portions: dict, mode: str) -> list[dict]:
    """One active-basis snapshot for cards, charts, tables and insight rankings."""
    if mode not in ("Per 100 g", "My portions"):
        raise ValueError("Unknown comparison basis")
    return [{"food_id": food["food_id"],
             **calculate_portion(food, 100.0 if mode == "Per 100 g" else portions[food["food_id"]]),
             "protein_density": protein_per_100_kcal(food)} for food in foods]
