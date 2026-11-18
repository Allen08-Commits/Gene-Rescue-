
"""GeneRescue AI - Main Application Controller."""

import importlib.util
import sys
from pathlib import Path

import streamlit as st


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="GeneRescue AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# 2. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
PAGES_DIR = BASE_DIR / "pages"
ASSETS_DIR = BASE_DIR / "assets"

CSS_PATH = ASSETS_DIR / "style.css"


# --------------------------------------------------
# 3. LOAD CUSTOM CSS
# --------------------------------------------------

if CSS_PATH.is_file():
    css = CSS_PATH.read_text(encoding="utf-8")

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# 4. INITIALIZE SESSION STATE
# --------------------------------------------------

DEFAULT_STATE = {
    "current_page": "welcome",
    "research_projects": [],
    "research_history": [],
    "research_evidence": [],
    "active_project": None,
}

for key, default_value in DEFAULT_STATE.items():

    if key not in st.session_state:

        if isinstance(default_value, list):
            st.session_state[key] = default_value.copy()

        else:
            st.session_state[key] = default_value


# --------------------------------------------------
# 5. PAGE MODULE LOADER
# --------------------------------------------------

def load_page(filename, module_name):
    """
    Load a Python page directly from the pages folder.
    This avoids importing page modules through
    'from pages import ...'.
    """

    file_path = PAGES_DIR / filename

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Required page file not found: {file_path}"
        )

    spec = importlib.util.spec_from_file_location(
        module_name,
        file_path,
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load page module: {filename}"
        )

    module = importlib.util.module_from_spec(spec)

    # Register module before execution
    sys.modules[module_name] = module

    spec.loader.exec_module(module)

    if not hasattr(module, "render"):
        raise AttributeError(
            f"{filename} must contain a render() function."
        )

    return module


# --------------------------------------------------
# 6. LOAD ALL RESEARCH PAGES
# --------------------------------------------------

welcome = load_page(
    "welcome.py",
    "generescue_welcome",
)

home = load_page(
    "home.py",
    "generescue_home",
)

sequence_analysis = load_page(
    "sequence_analysis.py",
    "generescue_sequence_analysis",
)

gene_discovery = load_page(
    "gene_discovery.py",
    "generescue_gene_discovery",
)

variant_analysis = load_page(
    "variant_analysis.py",
    "generescue_variant_analysis",
)

database_explorer = load_page(
    "database_explorer.py",
    "generescue_database_explorer",
)

functional_annotation = load_page(
    "functional_annotation.py",
    "generescue_functional_annotation",
)

crop_intelligence = load_page(
    "crop_intelligence.py",
    "generescue_crop_intelligence",
)


# --------------------------------------------------
# 7. NAVIGATION FUNCTION
# --------------------------------------------------

def navigate(page_name):
    """Change the current application page."""

    st.session_state["current_page"] = page_name

    st.rerun()


# --------------------------------------------------
# 8. PAGE ROUTING
# --------------------------------------------------

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


# --------------------------------------------------
# 9. VALIDATE CURRENT PAGE
# --------------------------------------------------

current_page = st.session_state.get(
    "current_page",
    "welcome",
)

if current_page not in PAGE_MAP:

    current_page = "welcome"

    st.session_state["current_page"] = "welcome"


# --------------------------------------------------
# 10. WORKSPACE HEADER
# --------------------------------------------------

if current_page not in ("welcome", "home"):

    header_col, button_col = st.columns(
        [5, 1]
    )

    with header_col:

        st.markdown(
            """
            <div class="brand-small">
                🌱 GeneRescue AI
            </div>
            """,
            unsafe_allow_html=True,
        )

    with button_col:

        if st.button(
            "Workspace",
            use_container_width=True,
        ):
            navigate("home")

    st.divider()


# --------------------------------------------------
# 11. RENDER SELECTED PAGE
# --------------------------------------------------

PAGE_MAP[current_page]()


# --------------------------------------------------
# 12. APPLICATION FOOTER
# --------------------------------------------------

if current_page != "welcome":

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:25px 0 10px 0;
            color:#829287;
            font-size:12px;
        ">
            GeneRescue AI |
            Intelligent Genetic Rescue System
            for Crop Improvement
        </div>
        """,
        unsafe_allow_html=True,
    )
