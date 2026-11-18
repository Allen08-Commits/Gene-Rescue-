
"""GeneRescue AI - Main application controller."""

import streamlit as st
from pathlib import Path

from pages import (
    welcome,
    home,
    sequence_analysis,
    gene_discovery,
    variant_analysis,
    database_explorer,
    functional_annotation,
    crop_intelligence,
)

st.set_page_config(
    page_title="GeneRescue AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Load application stylesheet
CSS_PATH = Path(__file__).parent / "assets" / "style.css"

if CSS_PATH.exists():
    st.markdown(
        f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

# Initialize temporary session data
DEFAULT_STATE = {
    "current_page": "welcome",
    "research_projects": [],
    "research_history": [],
    "research_evidence": [],
    "active_project": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, list) else value


def navigate(page):
    """Change the currently displayed page."""
    st.session_state["current_page"] = page
    st.rerun()


# Page routing
PAGE_MAP = {
    "welcome": welcome.render,
    "home": home.render,
    "sequence_analysis": sequence_analysis.render,
    "gene_discovery": gene_discovery.render,
    "variant_analysis": variant_analysis.render,
    "database_explorer": database_explorer.render,
    "functional_annotation": functional_annotation.render,
    "crop_intelligence": crop_intelligence.render,
}

current_page = st.session_state["current_page"]

if current_page not in PAGE_MAP:
    st.session_state["current_page"] = "welcome"
    current_page = "welcome"

# Navigation header for research pages
if current_page not in ("welcome", "home"):
    col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown(
            '<div class="brand-small">🌱 GeneRescue AI</div>',
            unsafe_allow_html=True,
        )

    with col2:
        if st.button("Workspace", use_container_width=True):
            navigate("home")

    st.divider()

# Render selected page
PAGE_MAP[current_page]()
