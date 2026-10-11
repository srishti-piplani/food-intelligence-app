"""Small, testable state transitions shared by Home and Food Explorer."""


def clear_selection(state) -> None:
    state.pop("selected_food", None)


def submit_search(state, query: str) -> None:
    state["search_query"] = query.strip()
    clear_selection(state)
    state["active_explorer_view"] = "Explore Foods"
    state["explorer_view"] = "Explore Foods"


def select_food(state, food_id: str) -> None:
    state["selected_food"] = food_id


def clear_search(state) -> None:
    state["food_query"] = ""
    submit_search(state, "")


def reset_filters(state) -> None:
    state["food_type"] = "All foods"
    state["saved_food_type"] = "All foods"


def remove_comparison(state, food_id=None) -> None:
    state["compare_foods"] = [item for item in state.get("compare_foods", []) if food_id is not None and item != food_id]
    state.pop("comparison_notice", None)


def set_view(state, view) -> None:
    state["active_explorer_view"] = view
    state["explorer_view"] = view


def add_comparison(state, food_id: str) -> None:
    selected = list(state.get("compare_foods", []))
    if food_id in selected:
        return
    if len(selected) >= 3:
        state["comparison_notice"] = "Your comparison has three foods. Remove one here or in Compare Foods to make room."
        return
    state["compare_foods"] = [*selected, food_id]
    state.pop("comparison_notice", None)
