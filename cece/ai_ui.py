"""Optional, click-only AI card; comparison remains fully usable offline."""

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from cece.ai_recommendations import (
    GOALS, RecommendationError, build_context, configuration,
    context_fingerprint, generate_take,
)


def _save_goal():
    st.session_state.saved_cece_goal = st.session_state.cece_goal


def _configuration():
    try:
        return configuration(st.secrets)
    except (StreamlitSecretNotFoundError, FileNotFoundError):
        return configuration()


def _show_response(saved, outdated):
    if outdated:
        st.warning("This take is outdated because your foods, goal, basis or portions changed. Ask CeCe again for a fresh take.")
    with st.container(key="cece_take_response", border=True):
        st.caption("Previous take · outdated" if outdated else "CeCe's recommendation")
        st.write(saved["text"])
        context = saved["context"]
        st.caption(f"For {context['goal']} · {context['comparison_basis']} · AI-generated with {saved['model']}")
        st.markdown("USDA sources: " + " · ".join(
            f"[{food['name']} · FDC {food['fdc_id']}]({food['source_url']})"
            for food in context["foods"]))


def render_ceces_take(foods, snapshot, portions, mode):
    with st.container(key="cece_take", border=True):
        st.subheader("CeCe's Take ✨")
        st.write("Not sure what to choose? Ask your food bestie!")
        st.session_state.setdefault("cece_goal", st.session_state.get("saved_cece_goal", GOALS[0]))
        goal = st.radio("What matters for this meal?", GOALS, horizontal=True,
                        key="cece_goal", on_change=_save_goal)
        context = build_context(foods, snapshot, portions, mode, goal)
        fingerprint = context_fingerprint(context)
        sufficient = 2 <= len(foods) <= 3
        if not sufficient:
            st.caption("Add at least two foods to hear CeCe's take!")
        clicked = st.button("Ask CeCe ✨", key="ask_cece", type="primary", disabled=not sufficient)
        if clicked and sufficient:
            try:
                key, model = _configuration()
                with st.spinner("CeCe's looking at your selected USDA records…"):
                    text = generate_take(context, key, model)
                st.session_state.cece_take_result = {
                    "text": text, "context": context, "fingerprint": fingerprint, "model": model,
                }
                st.session_state.pop("cece_take_error", None)
            except RecommendationError as error:
                st.session_state.cece_take_error = {"message": str(error), "fingerprint": fingerprint}
        error = st.session_state.get("cece_take_error")
        if error and error["fingerprint"] == fingerprint:
            st.info(error["message"])
        saved = st.session_state.get("cece_take_result")
        if saved:
            _show_response(saved, saved["fingerprint"] != fingerprint)
        st.caption("Uses your selected USDA records. General meal ideas are suggestions; this is not personalized medical advice.")
