
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
CSS_PATH = BASE_DIR / "assets" / "style.css"

st.set_page_config(
    page_title="GeneRescue AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_styles():
    if CSS_PATH.exists():
        css = CSS_PATH.read_text(encoding="utf-8")
        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )

load_styles()

# Shared application state
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("user", None)
st.session_state.setdefault("active_project", None)
st.session_state.setdefault("analysis_history", [])

# Hidden navigation: pages control their own visible navigation.
welcome = st.Page(
    "pages/welcome.py",
    title="Welcome",
    url_path="welcome",
    default=True
)

login = st.Page(
    "pages/login.py",
    title="Login",
    url_path="login"
)

register = st.Page(
    "pages/register.py",
    title="Create Account",
    url_path="register"
)

home = st.Page(
    "pages/home.py",
    title="Research Tools",
    url_path="home"
)

profile = st.Page(
    "pages/profile.py",
    title="Profile",
    url_path="profile"
)

sequence = st.Page(
    "pages/sequence_analysis.py",
    title="Sequence Analysis",
    url_path="sequence-analysis"
)

genes = st.Page(
    "pages/gene_discovery.py",
    title="Gene Discovery",
    url_path="gene-discovery"
)

variants = st.Page(
    "pages/variant_analysis.py",
    title="Variant Analysis",
    url_path="variant-analysis"
)

database = st.Page(
    "pages/database_explorer.py",
    title="Database Explorer",
    url_path="database-explorer"
)

functional = st.Page(
    "pages/functional_annotation.py",
    title="Functional Annotation",
    url_path="functional-annotation"
)

crop = st.Page(
    "pages/crop_intelligence.py",
    title="Crop Intelligence",
    url_path="crop-intelligence"
)

navigation = st.navigation(
    [
        welcome,
        login,
        register,
        home,
        profile,
        sequence,
        genes,
        variants,
        database,
        functional,
        crop
    ],
    position="hidden"
)

navigation.run()
