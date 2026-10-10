"""Pure gram-based portion scaling; missing nutrients stay missing."""

import math
from numbers import Real

from cece.data_access import NUTRIENTS


def calculate_portion(food: dict, grams: float) -> dict:
    """Scale a validated per-100-g record to a nonnegative gram portion."""
    if isinstance(grams, bool) or not isinstance(grams, Real) or not math.isfinite(grams) or grams < 0:
        raise ValueError("Portion must be a finite, nonnegative number of grams")
    if food.get("basis_g") != 100:
        raise ValueError("Expected a per-100-g food record")
    result = {"portion_g": grams}
    for name in NUTRIENTS:
        value = food[name]
        missing = value is None or (isinstance(value, Real) and math.isnan(value))
        if not missing and (not isinstance(value, Real) or not math.isfinite(value) or value < 0):
            raise ValueError(f"Invalid nutrient: {name}")
        result[name] = None if missing else value * grams / 100
        result[f"{name}_missing"] = missing
    return result
