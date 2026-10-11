"""Display formatting only; calculations and rankings retain full precision."""

import math
from numbers import Real


def nutrient_text(value, unit: str) -> str:
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        return "Unknown"
    if unit == "kcal":
        text = f"{value:,.1f}".removesuffix(".0")
    elif unit == "g / 100 kcal":
        text = f"{value:,.2f}"
    else:
        text = f"{value:,.2f}"
        if text.endswith("0"):
            text = text[:-1]  # retain at least one decimal for gram measurements
    return f"{text} {unit}"
