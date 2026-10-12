"""Food Explorer components; data operations remain in the core modules."""

import pandas as pd
import streamlit as st

from cece.data_access import DATA_DIR, NUTRIENTS, DETAIL_NUTRIENTS, load_foods, search_foods
from cece.nutrition import calculate_portion, comparison_snapshot, comparison_insights
from cece.food_labels import short_name, preparation_state, comparison_labels
from cece.imagery import image_metadata
from cece.charts import comparison_chart, PALETTE
from cece.explorer_state import clear_selection, select_food, clear_search, reset_filters, remove_comparison, set_view, add_comparison

from cece.presentation import nutrient_text
from cece.ai_ui import render_ceces_take

DETAIL_LABELS = {"total_sugars_g": "Total sugars", "added_sugars_g": "Added sugars", "saturated_fat_g": "Saturated fat", "trans_fat_g": "Trans fat", "sodium_mg": "Sodium", "cholesterol_mg": "Cholesterol"}

LABELS = {"calories_kcal": "Calories", "protein_g": "Protein", "carbohydrates_g": "Carbohydrates", "fat_g": "Fat", "fiber_g": "Fiber"}


@st.cache_data(show_spinner=False)
def _cached_foods(csv_stamp: int, manifest_stamp: int) -> pd.DataFrame:
    return load_foods()


def _select(food_id: str) -> None:
    select_food(st.session_state, food_id)


def _close_details() -> None:
    clear_selection(st.session_state)


def _add_comparison(food_id: str) -> None:
    add_comparison(st.session_state, food_id)


def _preparation_caption(food: dict, prefix="") -> None:
    state = preparation_state(food["description"])
    if state != "Not specified":
        st.caption(prefix + state)


def _source_details(food: dict) -> None:
    with st.expander("USDA Source Details"):
        st.write(food["description"])
        st.markdown(f"Source: **USDA FoodData Central** · FDC ID **{food['fdc_id']}** · {food['data_type']} · [Original record]({food['source_url']})")
        st.caption("Nutrition is from the October 10, 2026 local snapshot.")
        metadata = image_metadata(food)
        st.markdown(f"Image: {metadata['creator']} · [{metadata['source']}]({metadata.get('attribution_url', metadata['license_url'])}) · [{metadata['license']}]({metadata['license_url']})")
        st.caption(metadata.get("review_note", "Representative illustration, not the exact food or preparation."))
        if metadata.get("changes"):
            st.caption("Image modifications: " + metadata["changes"])


def _render_details(food: dict, indexed: dict) -> None:
    heading, close = st.columns([4, 1])
    heading.subheader("Nutrition Breakdown")
    close.button("Close", key="close_nutrition", on_click=_close_details, help="Close the selected food's nutrition panel")
    photo, name = st.columns([1, 1.6], vertical_alignment="center")
    with photo:
        st.image(image_metadata(food)["absolute_path"], width="stretch")
    with name:
        st.markdown(f"**{short_name(food['description'])}**")
        _preparation_caption(food, prefix="Preparation: ")
        st.caption(f"Branded · {food['brand']}" if food["data_type"] == "Branded" else "Generic food")
        added = food["food_id"] in st.session_state.get("compare_foods", [])
        with st.container(key="comparison_added" if added else "comparison_add"):
            st.button("Added to comparison ✓" if added else "Add to comparison",
                      key=f"add_compare_{food['food_id']}", on_click=_add_comparison,
                      args=(food["food_id"],), disabled=added, width="stretch")
        if added:
            st.button("Remove from comparison", key=f"explore_remove_{food['food_id']}", on_click=_remove, args=(food["food_id"],), width="stretch")
        elif len(st.session_state.get("compare_foods", [])) >= 3:
            st.caption("Three foods selected. Remove one below to make room.")
            labels = comparison_labels([indexed[i] for i in st.session_state.compare_foods])
            with st.expander("Manage comparison"):
                for selected_id in st.session_state.compare_foods:
                    st.button(f"Remove {labels[selected_id]}", key=f"manage_remove_{selected_id}", on_click=_remove, args=(selected_id,), width="stretch")
    st.caption(image_metadata(food).get("review_note", "Representative photograph") if image_metadata(food).get("kind") == "photograph" else "Photo unavailable · representative placeholder")
    grams = st.number_input(f"{short_name(food['description'])} — portion (g)", min_value=0.0, max_value=10000.0, value=float(st.session_state.get(f"saved_portion_{food['food_id']}", 100)), step=10.0, key=f"portion_{food['food_id']}", on_change=_save_detail_portion, args=(food["food_id"],))
    try:
        portion = calculate_portion(food, grams)
    except ValueError:
        st.warning("Please enter a finite, nonnegative portion in grams.")
        return
    with st.container(key="primary_calories"):
        value = portion["calories_kcal"]
        st.metric("Calories", "Unknown" if value is None else f"{value:,.1f} kcal")
    for names in (("protein_g", "carbohydrates_g"), ("fat_g", "fiber_g")):
        for col, nutrient in zip(st.columns(2), names):
            value = portion[nutrient]
            col.metric(LABELS[nutrient], "Unknown" if value is None else f"{value:,.1f} g")
    st.caption(f"For {grams:g} g. Unknown means not supplied, never zero.")
    with st.expander("Detailed Nutrition"):
        details = []
        for nutrient, (_, unit, _) in DETAIL_NUTRIENTS.items():
            value = portion[nutrient]
            details.append({"Nutrient": DETAIL_LABELS[nutrient], "Amount": "Unknown" if value is None else f"{value:,.2f} {unit}"})
        st.table(pd.DataFrame(details))
        st.caption("Added sugars are not derived from total sugars; fat subtypes may be missing.")
    _source_details(food)
    if food["data_type"] == "Branded":
        st.caption("Label-derived values may reflect rounding or an older product version.")


def _view_changed():
    st.session_state.active_explorer_view = st.session_state.explorer_view


def _open_explore():
    set_view(st.session_state, "Explore Foods")


def _clear_search():
    clear_search(st.session_state)


def _reset_filters():
    reset_filters(st.session_state)


def _filter_changed():
    st.session_state.saved_food_type = st.session_state.food_type


def _remove(food_id=None):
    remove_comparison(st.session_state, food_id)


def _save_control(key):
    st.session_state[f"saved_{key}"] = st.session_state[key]


def _save_detail_portion(food_id):
    st.session_state[f"saved_portion_{food_id}"] = st.session_state[f"portion_{food_id}"]


def _save_portion(food_id):
    st.session_state[f"saved_compare_portion_{food_id}"] = st.session_state[f"compare_portion_{food_id}"]


def render_explorer(render_search) -> None:
    st.session_state.setdefault("explorer_view", st.session_state.get("active_explorer_view", "Explore Foods"))
    count = len(st.session_state.get("compare_foods", []))
    with st.container(key="explorer_navigation"):
        view = st.radio("Food Explorer views", ["Explore Foods", "Compare Foods"], horizontal=True,
                        key="explorer_view", on_change=_view_changed, label_visibility="collapsed",
                        format_func=lambda v: f"Compare Foods ({count})" if v == "Compare Foods" else v)

    try:
        foods = _cached_foods((DATA_DIR / "foods.csv").stat().st_mtime_ns, (DATA_DIR / "manifest.json").stat().st_mtime_ns)
    except (OSError, ValueError, KeyError) as error:
        st.error("CeCe couldn’t load the verified food dataset. Please check or regenerate the local data files.")
        with st.expander("Data error details"):
            st.code(str(error))
        return
    results = search_foods(foods, st.session_state.get("search_query", st.session_state.get("food_query", "")))
    indexed = {row["food_id"]: row for row in foods.to_dict("records")}
    if view == "Compare Foods":
        _render_comparison(indexed)
        return
    discovery, detail = st.columns([1.15, 1], gap="large")
    with discovery:
        render_search()
        clear, reset = st.columns(2)
        clear.button("Clear Search", key="clear_search", on_click=_clear_search, width="stretch")
        reset.button("Reset Filters", key="reset_filters", on_click=_reset_filters, width="stretch")
        with st.expander("Filters"):
            st.session_state.setdefault("food_type", st.session_state.get("saved_food_type", "All foods"))
            kind = st.selectbox("Food type", ["All foods", "Generic foods", "Branded products"], key="food_type", on_change=_filter_changed)
        if kind != "All foods":
            results = results[results.data_type.eq("Branded") if kind == "Branded products" else results.data_type.ne("Branded")]
        if st.session_state.get("selected_food") not in set(results.food_id):
            clear_selection(st.session_state)
        st.caption(f"{len(results)} foods · verified USDA sample")
        if results.empty:
            st.info("No matching foods yet. Try tofu, lentils, yogurt, or Quaker. This small sample doesn’t cover every food or product.")
        else:
            with st.container(height=570, key="discovery_results"):
                for food in results.to_dict("records"):
                    selected = st.session_state.get("selected_food") == food["food_id"]
                    with st.container(border=True, key="selected_result" if selected else f"result_{food['food_id']}"):
                        photo, text, action = st.columns([1, 2.1, 1.3], vertical_alignment="center")
                        metadata = image_metadata(food)
                        with photo:
                            st.image(metadata["thumbnail_absolute_path"], width="stretch")
                        with text:
                            st.markdown(f"**{short_name(food['description'])}**")
                            _preparation_caption(food)
                            st.caption(f"Branded · {food['brand']}" if food["data_type"] == "Branded" else "Generic food")
                            st.caption("Representative photo" if metadata.get("kind") == "photograph" else "Photo unavailable")
                        with action:
                            st.button("Selected ✓" if selected else "View nutrition", key=f"view_{food['food_id']}", type="primary" if selected else "secondary", on_click=_select, args=(food["food_id"],), width="stretch")
    if st.session_state.get("comparison_notice"):
        st.warning(st.session_state.comparison_notice)
    with detail:
        with st.container(border=True, key="nutrition_panel"):
            selected = indexed.get(st.session_state.get("selected_food"))
            if selected:
                _render_details(selected, indexed)
            else:
                st.image(str(DATA_DIR.parent / "assets/cece-portrait.png"), width=110)
                st.subheader("Your next bite, a little clearer")
                st.write("Choose a food on the left to explore its nutrition.")
                st.caption("Adjust your portion, discover the details, and compare your favorites. CeCe’s here to help. ♡")


def _render_comparison(indexed: dict) -> None:
    ids = list(st.session_state.get("compare_foods", []))
    labels = comparison_labels([indexed[i] for i in ids])
    take_slot = st.container()  # Rendered first, populated with the current snapshot below.
    add, clear = st.columns([3, 1])
    add.button("← Explore foods · add another", on_click=_open_explore)
    clear.button("Clear Comparison", key="clear_comparison", on_click=_remove, width="stretch", type="primary", disabled=not ids)
    for key, default in (("comparison_basis", "Per 100 g"), ("comparison_nutrient", "Calories"), ("protein_density", False)):
        st.session_state.setdefault(key, st.session_state.get(f"saved_{key}", default))
    mode = st.radio("Compare amounts", ["Per 100 g", "My portions"], horizontal=True, key="comparison_basis", on_change=_save_control, args=("comparison_basis",))
    basis = "per 100 g" if mode == "Per 100 g" else "selected portions"
    st.caption(f"Comparing {basis}. Edit portions below; they apply when My portions is selected.")
    rows, portions, metric_slots = [], {}, {}
    if ids:
        for col, food_id in zip(st.columns(len(ids)), ids):
            food = indexed[food_id]
            with col, st.container(border=True, key=f"comparison_card_{food_id}"):
                st.image(image_metadata(food)["thumbnail_absolute_path"], width="stretch")
                st.markdown(f"**{labels[food_id]}**")
                _preparation_caption(food)
                st.caption(f"Branded · {food['brand']}" if food['data_type'] == 'Branded' else 'Generic food')
                grams = st.number_input(f"{labels[food_id]} — portion (g)", min_value=0.0, max_value=10000.0,
                    value=float(st.session_state.get(f"saved_compare_portion_{food_id}", st.session_state.get(f"saved_portion_{food_id}", st.session_state.get(f"portion_{food_id}", 100)))),
                    step=10.0, key=f"compare_portion_{food_id}", on_change=_save_portion, args=(food_id,))
                portions[food_id] = grams
                st.caption("Values per 100 g" if mode == "Per 100 g" else f"Values for {grams:g} g")
                metric_slots[food_id] = st.container()
                st.button("Remove", key=f"remove_{food_id}", on_click=_remove, args=(food_id,), width="stretch")
    try:
        snapshot = comparison_snapshot([indexed[i] for i in ids], portions, mode)
    except ValueError:
        st.warning("Please enter finite, nonnegative portions.")
        return
    with take_slot:
        render_ceces_take([indexed[i] for i in ids], snapshot, portions, mode)
    for food_id, values in zip(ids, snapshot):
        food = indexed[food_id]
        row = {"Food": labels[food_id], "Description": food['description'], "Portion (g)": values['portion_g'], **{LABELS[n]: values[n] for n in NUTRIENTS}}
        rows.append({**row, **values})
        with metric_slots[food_id]:
            st.metric("Calories", nutrient_text(values['calories_kcal'], "kcal"))
            for names in (("protein_g", "carbohydrates_g"), ("fat_g", "fiber_g")):
                for cell, name in zip(st.columns(2), names):
                    cell.metric(LABELS[name], nutrient_text(values[name], "g"))
    if len(ids) < 2:
        st.info("Add at least two foods to discover how their nutrition compares. Explore a food, then choose Add to comparison.")
        return
    states = {preparation_state(indexed[i]['description']) for i in ids}
    if len(states - {"Not specified"}) > 1:
        st.info("These foods have different preparation states. Water content and preparation can change nutrition per 100 g.")
    if "Not specified" in states:
        st.caption("USDA does not specify preparation for at least one food.")
    frame = pd.DataFrame(rows)
    colors = {labels[i]: PALETTE[n] for n, i in enumerate(ids)}
    with st.container(border=True, key="comparison_area"):
        selector, density = st.columns([2, 1])
        nutrient = selector.selectbox("Nutrient", ["Calories", "Protein", "Carbs", "Fat", "Fiber"], key="comparison_nutrient", on_change=_save_control, args=("comparison_nutrient",))
        density_mode = density.checkbox("Show protein per 100 kcal", key="protein_density", on_change=_save_control, args=("protein_density",))
        nutrient = "Carbohydrates" if nutrient == "Carbs" else nutrient
        unit = "kcal" if nutrient == "Calories" else "g"
        title = f"{nutrient} · {basis}"
        if density_mode:
            nutrient, unit, title = "protein_density", "g / 100 kcal", "Protein per 100 kcal"
            st.caption("Protein density uses source values, independent of portion size; positive known calories and known protein are required.")
        if frame[nutrient].notna().any():
            st.plotly_chart(comparison_chart(frame, nutrient, title, unit, colors), width="stretch", config={"displaylogo": False})
        else:
            st.info("This nutrient is Unknown for all selected foods.")
        for row in rows:
            if row[nutrient] is None:
                st.caption(f"{row['Food']}: Unknown · excluded from this chart")
        st.caption("Labels are rounded for readability; the table preserves calculated values. Unknown is never zero.")
    with st.container(key="comparison_insights"):
        st.subheader("A little food clarity")
        st.caption(f"Nutrient observations: {basis}. Protein per 100 kcal is independent of portion size.")
        insights = comparison_insights(rows)
        icons = ("💪", "🌿", "☀", "⚖")
        for offset in (0, 2):
            for index, col in enumerate(st.columns(2), start=offset):
                insight = insights[index]
                with col, st.container(border=True, key=f"insight_{index}"):
                    title = "Most protein for your calories" if index == 3 else insight["title"]
                    st.markdown(f"{icons[index]} **{title}**")
                    if insight['value'] is None:
                        st.write("Unknown for all selected foods")
                    else:
                        st.markdown("**" + " · ".join(insight['foods']) + (" (tie)" if len(insight['foods']) > 1 else "") + "**")
                        if index == 3:
                            st.metric("g protein per 100 kcal", f"{insight['value']:,.2f}")
                            st.caption("Highest protein density among your selected foods with known values.")
                        else:
                            st.metric("Per 100 g" if mode == "Per 100 g" else "My portions", nutrient_text(insight['value'], insight['unit']))
                        if insight['known_count'] < insight['total_count']:
                            st.caption(f"Among {insight['known_count']} foods with known values; {insight['total_count'] - insight['known_count']} Unknown excluded.")
    with st.expander("Detailed comparison table"):
        columns = ['Food', 'Portion (g)', *LABELS.values()]
        st.dataframe(frame[columns], hide_index=True, width="stretch")
        st.caption("Calories: kcal. Protein, carbohydrates, fat and fiber: g. Blank cells mean Unknown.")
    with st.expander("Comparison source details"):
        for food_id in ids:
            st.markdown(f"**{labels[food_id]}**")
            _source_details(indexed[food_id])
