"""Consumer-facing Streamlit shell with a verified local Food Explorer."""

from pathlib import Path
import base64

import streamlit as st

from cece.explorer_ui import render_explorer
from cece.explorer_state import submit_search

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = (
    "Home",
    "Food Explorer",
    "Personal Food Profile",
    "Meal Builder",
    "Restaurant Finder",
    "Pantry",
    "Festival Foods",
    "AI Food Assistant",
)
NAV_ICONS = dict(
    zip(
        SECTIONS,
        (
            "home",
            "search",
            "person",
            "restaurant",
            "location_on",
            "inventory_2",
            "redeem",
            "chat_bubble",
        ),
    )
)
DESCRIPTIONS = {
    "Food Explorer": "Search foods, understand nutrition, and compare your options.",
    "Personal Food Profile": "Your preferences, dietary needs, and goals, all in one place.",
    "Meal Builder": "Create balanced meals that fit your goals.",
    "Restaurant Finder": "Discover places to eat with confidence.",
    "Pantry": "Turn what you have into something amazing.",
    "Festival Foods": "Explore traditional favorites and dietary-friendly adaptations.",
    "AI Food Assistant": "A little personalized help with everyday food decisions.",
}
CARDS = (
    ("Food Explorer", "food-explorer", "Explore foods"),
    ("Meal Builder", "meal-builder", "Build a meal"),
    ("Restaurant Finder", "restaurant-finder", "Find a place"),
    ("Pantry", "pantry", "Open pantry"),
    ("Festival Foods", "festival-foods", "Explore traditions"),
)


def _navigate(section: str) -> None:
    st.session_state.section = section


def _suggest(query: str) -> None:
    st.session_state.food_query = query
    submit_search(st.session_state, query)
    _navigate("Food Explorer")


def _query_changed() -> None:
    submit_search(st.session_state, st.session_state.get("food_query", ""))
    _navigate("Food Explorer")


def _search_clicked() -> None:
    _query_changed()
    _navigate("Food Explorer")


def _render_sidebar_navigation() -> str:
    """Render native navigation controls with consistent icon/label/badge rows."""
    st.session_state.setdefault("section", "Home")
    section = st.session_state.section
    with st.container(key="sidebar_navigation"):
        for name in SECTIONS:
            active = name == section
            with st.container(
                key=f"nav_active_{name}" if active else f"nav_row_{name}"
            ):
                label, badge = st.columns(
                    [8, 1.5], gap="small", vertical_alignment="center"
                )
                with label:
                    st.button(
                        name,
                        icon=f":material/{NAV_ICONS[name]}:",
                        key=f"nav_{name}",
                        type="primary" if active else "tertiary",
                        width="stretch",
                        on_click=_navigate,
                        args=(name,),
                        help=(
                            "Current page"
                            if active
                            else (
                                f"Open {name}"
                                if name in ("Home", "Food Explorer")
                                else f"{name} · Coming Soon"
                            )
                        ),
                    )
                with badge:
                    if name not in ("Home", "Food Explorer"):
                        st.html(
                            '<div class="nav-badge-slot"><span class="nav-soon">Soon</span></div>'
                        )
                    else:
                        st.html(
                            '<div class="nav-badge-slot"><span class="nav-soon nav-soon-empty" aria-hidden="true">Soon</span></div>'
                        )
    return section


def render_app() -> None:
    st.set_page_config(
        page_title="CeCe — Your Food Bestie", page_icon="🍑", layout="wide"
    )
    pattern = base64.b64encode((ROOT / "assets/food-pattern.svg").read_bytes()).decode(
        "ascii"
    )
    styles = (
        (ROOT / "cece/styles.css")
        .read_text()
        .replace("__FOOD_PATTERN_URL__", "data:image/svg+xml;base64," + pattern)
    )
    st.markdown(f"<style>{styles}</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.image(str(ROOT / "assets/cece-portrait.png"), width=145)
        st.markdown(
            '<div class="brand">CeCe</div><p class="brand-subtitle">Your Food Bestie</p>',
            unsafe_allow_html=True,
        )
        section = _render_sidebar_navigation()
        st.markdown(
            '<div class="sidebar-note">🌿<br>Good food fuels<br>a happier you!<br><span>♡</span></div>',
            unsafe_allow_html=True,
        )
        with st.expander("About CeCe"):
            st.write(
                "Your food journey, your way. A local preview of your future food companion."
            )

    st.title("CeCe — Your Food Bestie")
    if section in ("Home", "Food Explorer"):
        _render_home(section)
    else:
        _render_coming_soon(section)
    with st.expander("Our promise: clear data, honest answers"):
        st.write(
            "Nutrition records preserve USDA FDC ID, data type, and source information."
        )
        st.write(
            "Dietary status will distinguish confirmed compatibility, known conflict, and unknown. Missing allergen or gluten information never proves safety."
        )
        st.caption(
            "Nutrition comes from a curated 36-food USDA snapshot. CeCe's Take provides optional AI comparison explanations; dietary safety classifications are not implemented."
        )


def _render_home(section: str) -> None:
    if section == "Home":
        with st.container(key="hero"):
            left, right = st.columns([1.65, 1], vertical_alignment="center")
            with left:
                st.markdown(
                    '<p class="handwritten greeting">Hey there!</p><h2 class="hero-heading">What’s on your mind<br><span>(or plate)?</span></h2><p class="hero-copy">Craving something? Curious about nutrition?<br>CeCe’s got you.</p>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<p class="tagline">Hungry? Ask CeCe.</p>', unsafe_allow_html=True
                )
            with right:
                st.image(str(ROOT / "assets/cece-hero.png"), width="stretch")
    if section == "Home":
        render_search()

    st.header("Food Explorer" if section == "Food Explorer" else "Explore with CeCe")
    if section == "Home":
        st.markdown(
            '<p class="journey handwritten">Your food journey, your way ♡</p>',
            unsafe_allow_html=True,
        )
    if section == "Food Explorer":
        render_explorer(render_search)
    if section == "Food Explorer":
        return
    with st.container(key="feature_cards"):
        for col, (name, asset, cta) in zip(st.columns(5), CARDS):
            with col:
                with st.container(border=True):
                    st.image(str(ROOT / f"assets/{asset}.png"), width="stretch")
                    st.subheader(name)
                    st.write(DESCRIPTIONS[name])
                    st.button(
                        f"{cta} →",
                        key=f"card_{asset}",
                        on_click=_navigate,
                        args=(name,),
                        width="stretch",
                    )
                    st.caption(
                        "Ready to explore" if name == "Food Explorer" else "Coming Soon"
                    )
    with st.container(key="encouragement"):
        first, second, third = st.columns([1.2, 1, 1])
        with first:
            st.markdown(
                '<div class="quote green">Good food<br>brighter days <span>♡</span></div>',
                unsafe_allow_html=True,
            )
        with second:
            st.markdown(
                '<div class="quote cream">“Food is not just fuel,<br>it’s a little bit of happiness every day.”<br><small>– CeCe ♡</small></div>',
                unsafe_allow_html=True,
            )
        with third:
            st.markdown(
                '<div class="quote peach">🌿 Build a healthier, happier you,<br>one meal at a time.</div>',
                unsafe_allow_html=True,
            )
    st.subheader("Search inspiration")
    st.caption("Explore more of our verified food sample.")
    for col, query in zip(st.columns(4), ("edamame", "rice", "oats", "Chobani")):
        col.button(
            query,
            key=f"inspiration_{query}",
            on_click=_suggest,
            args=(query,),
            width="stretch",
        )


def _render_coming_soon(section: str) -> None:
    st.header(section)
    st.info("Coming Soon")
    with st.container(key="coming_soon", border=True):
        art, content = st.columns([1, 2], vertical_alignment="center")
        with art:
            st.image(str(ROOT / "assets/cece-portrait.png"), width=180)
        with content:
            st.markdown(
                '<p class="handwritten">Something delicious is on its way…</p>',
                unsafe_allow_html=True,
            )
            st.write(DESCRIPTIONS[section])
            st.caption(
                "CeCe is still growing. This feature is planned and isn’t available yet."
            )
            st.button(
                "Back to Home →", on_click=_navigate, args=("Home",), type="primary"
            )


def render_search() -> None:
    if "food_query" not in st.session_state:
        st.session_state.food_query = st.session_state.get("search_query", "")
    with st.container(key="food_search_bar", border=True):
        entry, action = st.columns([5, 1], vertical_alignment="bottom")
        with entry:
            st.text_input(
                "Search foods, brands, or ingredients",
                key="food_query",
                placeholder="🔍  What sounds good? Search foods, brands, or ingredients…",
                label_visibility="collapsed",
                on_change=_query_changed,
            )
        with action:
            st.button(
                "Search", type="primary", width="stretch", on_click=_search_clicked
            )
        suggestions = st.columns(5)
        for col, query in zip(
            suggestions,
            ("tofu", "cooked lentils", "Greek yogurt", "Quaker", "chickpeas"),
        ):
            col.button(
                query,
                key=f"suggest_{query}",
                on_click=_suggest,
                args=(query,),
                width="stretch",
            )
