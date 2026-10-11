"""Source-derived presentation labels; never dietary classifications."""

import re
from collections import Counter


def preparation_state(description: str) -> str:
    text = description.casefold()
    states = [word for word in ("raw", "cooked", "dry", "frozen", "canned", "drained", "baked", "boiled", "unprepared") if re.search(rf"\b{word}\b", text)]
    if "edamame" in text and re.search(r"\bprepared\b", text):
        states.append("prepared")
    return ", ".join(states) or "Not specified"


def short_name(description: str) -> str:
    """Keep defining variants; do not infer a cooking state from ingredient processing."""
    text = description.casefold()
    if "surimi" in text:
        return "Surimi with tofu & edamame"
    if "pasta" in text:
        return "Chickpea & lentil pasta"
    if "granola bar" in text:
        return "Granola bar"
    if "greek oats yogurt" in text:
        return "Banana maple oat yogurt"
    if "tofu" in text:
        variant = "Firm" if "firm" in text else "Soft" if "soft" in text else "Nigari" if "nigari" in text else ""
        return f"{variant} tofu".strip().capitalize()
    if "edamame" in text:
        return "Edamame"
    if "oats" in text:
        return "Dry oats" if re.search(r"\bdry\b", text) else "Cooked oatmeal" if "cooked" in text else "Oats"
    if "yogurt" in text:
        fat = "nonfat" if "nonfat" in text else "low-fat" if ("low fat" in text or "lowfat" in text) else "whole-milk"
        return f"{'Greek' if 'greek' in text else 'Plain'} yogurt · {fat}"
    if "rice" in text:
        return f"Cooked {'brown' if 'brown' in text else 'white'} rice" if "cooked" in text else "Rice"
    simple = {"quinoa": "quinoa", "lentils": "lentils", "chickpeas": "chickpeas", "beans, black": "black beans", "spinach": "spinach", "sweet potato": "sweet potato", "apples": "Fuji apple", "broccoli": "Broccoli", "carrots": "Carrot", "tomatoes": "Tomato", "bananas": "Banana", "avocados": "Avocado", "egg, whole": "Whole egg", "milk, reduced": "Milk · 2%", "oil, olive": "Olive oil"}
    for needle, name in simple.items():
        if needle in text:
            prefix = "Cooked " if "cooked" in text else "Canned " if "canned" in text else ""
            return prefix + name if prefix else name.capitalize()
    return description.split("(")[0].split(",")[0].strip().capitalize()


def comparison_labels(foods: list[dict]) -> dict[str, str]:
    """Disambiguate only when names collide, using preparation then record ID."""
    labels = {food['food_id']: ((str(food['brand']) + " · ") if food['data_type'] == 'Branded' else "") + short_name(food['description']) for food in foods}
    counts = Counter(labels.values())
    for food in foods:
        key = food['food_id']
        if counts[labels[key]] > 1:
            state = preparation_state(food["description"])
            if state != "Not specified":
                labels[key] += " · " + state
    counts = Counter(labels.values())
    for food in foods:
        key = food['food_id']
        if counts[labels[key]] > 1:
            labels[key] += f" · record {food['fdc_id']}"
    return labels
