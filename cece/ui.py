"""Consumer-facing Streamlit shell; all food capabilities remain planned."""

from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = (
    "Home", "Food Explorer", "Personal Food Profile", "Meal Builder",
    "Restaurant Finder", "Pantry", "Festival Foods", "AI Food Assistant",
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
    st.session_state.submitted_query = query


def render_app() -> None:
    st.set_page_config(page_title="CeCe — Your Food Bestie", page_icon="🍑", layout="wide")
    st.markdown(f"<style>{(ROOT / 'cece' / 'styles.css').read_text()}</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.image(str(ROOT / "assets/cece-portrait.png"), width=145)
        st.markdown('<div class="brand">CeCe</div><p class="brand-subtitle">Your Food Bestie</p>', unsafe_allow_html=True)
        section = st.radio("Explore CeCe", SECTIONS, key="section", label_visibility="collapsed")
        st.markdown('<div class="sidebar-note">🌿<br>Good food fuels<br>a happier you!<br><span>♡</span></div>', unsafe_allow_html=True)
        with st.expander("About CeCe"):
            st.write("Your food journey, your way. A local preview of your future food companion.")

    st.title("CeCe — Your Food Bestie")
    if section in ("Home", "Food Explorer"):
        _render_home(section)
    else:
        _render_coming_soon(section)
    with st.expander("Our promise: clear data, honest answers"):
        st.write("Future nutrition records will preserve USDA FDC ID, data type, and source information.")
        st.write("Dietary status will distinguish confirmed compatibility, known conflict, and unknown. Missing allergen or gluten information never proves safety.")
        st.caption("No food dataset, nutrition values, or dietary classifications are loaded in this preview.")


def _render_home(section: str) -> None:
    with st.container(key="hero"):
        left, right = st.columns([1.65, 1], vertical_alignment="center")
        with left:
            st.markdown('<p class="handwritten greeting">Hey there!</p><h2 class="hero-heading">What’s on your mind<br><span>(or plate)?</span></h2><p class="hero-copy">Craving something? Curious about nutrition?<br>CeCe’s got you.</p>', unsafe_allow_html=True)
            st.markdown('<p class="handwritten tagline">Hungry? Ask CeCe.</p>', unsafe_allow_html=True)
        with right:
            st.image(str(ROOT / "assets/cece-hero.png"), width="stretch")
        with st.form("food_search", border=False):
            entry, action = st.columns([5, 1], vertical_alignment="bottom")
            with entry:
                st.text_input("Search foods, brands, or ingredients", key="food_query", placeholder="Search for foods, brands, or ingredients…", label_visibility="collapsed")
            with action:
                submitted = st.form_submit_button("Search", type="primary", width="stretch")
        if submitted:
            st.session_state.submitted_query = st.session_state.food_query.strip()
        st.caption("Try searching:")
        suggestions = st.columns(5)
        for col, query in zip(suggestions, ("tofu", "cooked lentils", "Greek yogurt", "Quaker oats", "chickpeas")):
            col.button(query, key=f"suggest_{query}", on_click=_suggest, args=(query,), width="stretch")
        if "submitted_query" in st.session_state:
            query = st.session_state.submitted_query
            if query:
                st.info(f'Food search is Coming Soon. You entered “{query}”. No food results are available yet.')
            else:
                st.warning("Add a food, brand, or ingredient to get started.")

    st.header("Food Explorer" if section == "Food Explorer" else "Explore with CeCe")
    st.markdown('<p class="journey handwritten">Your food journey, your way ♡</p>', unsafe_allow_html=True)
    with st.container(key="feature_cards"):
        for col, (name, asset, cta) in zip(st.columns(5), CARDS):
            with col:
                with st.container(border=True):
                    st.image(str(ROOT / f"assets/{asset}.png"), width="stretch")
                    st.subheader(name)
                    st.write(DESCRIPTIONS[name])
                    st.button(f"{cta} →", key=f"card_{asset}", on_click=_navigate, args=(name,), width="stretch")
                    st.caption("Coming Soon")
    with st.container(key="encouragement"):
        first, second, third = st.columns([1.2, 1, 1])
        with first:
            st.markdown('<div class="quote green">Good food<br>brighter days <span>♡</span></div>', unsafe_allow_html=True)
        with second:
            st.markdown('<div class="quote cream">“Food is not just fuel,<br>it’s a little bit of happiness every day.”<br><small>– CeCe ♡</small></div>', unsafe_allow_html=True)
        with third:
            st.markdown('<div class="quote peach">🌿 Build a healthier, happier you,<br>one meal at a time.</div>', unsafe_allow_html=True)
    st.subheader("Search inspiration")
    st.caption("Ideas to try when Food Explorer launches — these are not verified dietary categories.")
    for col, query in zip(st.columns(4), ("High protein foods", "Low calorie snacks", "Indian foods", "Breakfast ideas")):
        col.button(query, key=f"inspiration_{query}", on_click=_suggest, args=(query,), width="stretch")


def _render_coming_soon(section: str) -> None:
    st.header(section)
    st.info("Coming Soon")
    with st.container(key="coming_soon", border=True):
        art, content = st.columns([1, 2], vertical_alignment="center")
        with art:
            st.image(str(ROOT / "assets/cece-portrait.png"), width=180)
        with content:
            st.markdown('<p class="handwritten">Something delicious is on its way…</p>', unsafe_allow_html=True)
            st.write(DESCRIPTIONS[section])
            st.caption("CeCe is still growing. This feature is planned and isn’t available yet.")
            st.button("Back to Home →", on_click=_navigate, args=("Home",), type="primary")
