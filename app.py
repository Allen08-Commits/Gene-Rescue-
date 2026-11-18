
"""GeneRescue AI - Main application."""

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="GeneRescue AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Load application styling
CSS_PATH = Path(__file__).parent / "assets" / "style.css"

if CSS_PATH.exists():
    st.markdown(
        f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

# Initialize session-only application state
DEFAULT_STATE = {
    "active_project": None,
    "research_history": [],
    "research_evidence": [],
    "research_projects": [],
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Hidden multipage navigation
pages = [
    st.Page(
        "pages/welcome.py",
        title="Welcome",
        default=True,
    ),
    st.Page(
        "pages/home.py",
        title="Research Workspace",
    ),
    st.Page(
        "pages/sequence_analysis.py",
        title="Sequence Analysis",
    ),
    st.Page(
        "pages/gene_discovery.py",
        title="Gene Discovery",
    ),
    st.Page(
        "pages/variant_analysis.py",
        title="Variant Analysis",
    ),
    st.Page(
        "pages/database_explorer.py",
        title="Database Explorer",
    ),
    st.Page(
        "pages/functional_annotation.py",
        title="Functional Annotation",
    ),
    st.Page(
        "pages/crop_intelligence.py",
        title="Crop Intelligence",
    ),
]

navigation = st.navigation(
    pages,
    position="hidden",
)

navigation.run()
