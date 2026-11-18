
"""GeneRescue AI - Main Application."""

import importlib.util
import sys
from pathlib import Path

import streamlit as st


# ==================================================
# 1. APPLICATION CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="GeneRescue AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
PAGES_DIR = BASE_DIR / "pages"
ASSETS_DIR = BASE_DIR / "assets"


# ==================================================
# 2. LOAD CSS
# ==================================================

CSS_PATH = ASSETS_DIR / "style.css"

if CSS_PATH.is_file():
    css = CSS_PATH.read_text(encoding="utf-8")
    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


# ==================================================
# 3. SESSION STATE
# ==================================================

DEFAULT_STATE = {
    "current_page": "welcome",
    "research_projects": [],
    "research_history": [],
    "research_evidence": [],
    "active_project": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = (
            value.copy() if isinstance(value, list) else value
        )


# ==================================================
# 4. FIND PAGE FILES
# ==================================================

def find_page_file(filename):
    """
    Find a page file in the repository.
    First checks pages/, then searches the repository.
    """

    expected = PAGES_DIR / filename

    if expected.is_file():
        return expected

    # Case-insensitive search in the pages folder
    if PAGES_DIR.is_dir():
        for item in PAGES_DIR.iterdir():
            if item.is_file() and item.name.lower() == filename.lower():
                return item

    # Search other repository folders as a fallback
    for item in BASE_DIR.rglob("*"):
        if not item.is_file():
            continue

        if ".git" in item.parts or ".venv" in item.parts:
            continue

        if item.name.lower() == filename.lower():
            return item

    return None


# ==================================================
# 5. IMPORT PAGE MODULES
# ==================================================

def load_page(filename, module_name):
    file_path = find_page_file(filename)

    if file_path is None:
        raise FileNotFoundError(
            f"Cannot find {filename}. "
            f"Expected location: {PAGES_DIR / filename}. "
            "Check that the file is committed to the deployed GitHub branch."
        )

    spec = importlib.util.spec_from_file_location(
        module_name,
        file_path,
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Cannot create an import specification for {file_path}"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    if not callable(getattr(module, "render", None)):
        raise AttributeError(
            f"{filename} must define a callable render() function."
        )

    return module


# ==================================================
# 6. LOAD ALL EIGHT PAGES
# ==================================================

PAGE_FILES = {
    "welcome": "welcome.py",
    "home": "home.py",
    "sequence_analysis": "sequence_analysis.py",
    "gene_discovery": "gene_discovery.py",
    "variant_analysis": "variant_analysis.py",
    "database_explorer": "database_explorer.py",
    "functional_annotation": "functional_annotation.py",
    "crop_intelligence": "crop_intelligence.py",
}

PAGE_MODULES = {}

missing_pages = []

for page_key, filename in PAGE_FILES.items():
    try:
        PAGE_MODULES[page_key] = load_page(
            filename,
            f"generescue_{page_key}",
        )
    except FileNotFoundError:
        missing_pages.append(filename)


# ==================================================
# 7. NAVIGATION
# ==================================================

def navigate(page_name):
    if page_name in PAGE_FILES:
        st.session_state["current_page"] = page_name
        st.rerun()


# ==================================================
# 8. CHECK REQUIRED FILES
# ==================================================

if missing_pages:
    st.error("Some research page files are missing.")

    st.write(
        "The following files could not be located in the deployed repository:"
    )

    for filename in missing_pages:
        st.code(f"pages/{filename}")

    st.info(
        "Please ensure these files are committed to the same GitHub "
        "repository and branch used by Streamlit."
    )

    st.stop()


# ==================================================
# 9. PAGE ROUTING
# ==================================================

PAGE_MAP = {
    name: module.render
    for name, module in PAGE_MODULES.items()
}

current_page = st.session_state.get(
    "current_page",
    "welcome",
)

if current_page not in PAGE_MAP:
    current_page = "welcome"
    st.session_state["current_page"] = current_page


# ==================================================
# 10. WORKSPACE HEADER
# ==================================================

if current_page not in ("welcome", "home"):

    header_col, button_col = st.columns([5, 1])

    with header_col:
        st.markdown(
            '<div class="brand-small">🌱 GeneRescue AI</div>',
            unsafe_allow_html=True,
        )

    with button_col:
        if st.button("Workspace", use_container_width=True):
            navigate("home")

    st.divider()


# ==================================================
# 11. RENDER PAGE
# ==================================================

PAGE_MAP[current_page]()


# ==================================================
# 12. FOOTER
# ==================================================

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
