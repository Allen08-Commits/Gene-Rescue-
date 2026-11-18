
import streamlit as st

def require_login():
    if not st.session_state.get("authenticated"):
        st.warning("Please log in to access your research workspace.")
        st.switch_page("pages/login.py")
        st.stop()

require_login()

user = st.session_state.get("user") or {}
username = user.get("username", "Researcher")

# Top navigation
top_left, top_right = st.columns([5, 1])

with top_left:
    st.markdown(
        """
        <div style="padding:8px 0;">
            <span style="font-size:27px;">🌱</span>
            <span style="font-size:24px;font-weight:800;color:#24563C;">
                GeneRescue AI
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

with top_right:
    if st.button("👤 Profile", use_container_width=True):
        st.switch_page("pages/profile.py")

st.divider()

st.markdown(
    f"""
    <div style="padding:12px 0 22px;">
        <h1 style="font-size:2.1rem;">Welcome, {username}</h1>
        <p style="color:#718078;">
            Select a research tool to begin your investigation.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

tools = [
    {
        "name": "Sequence Analysis",
        "description": "Investigate DNA, RNA and protein sequences through computational analysis.",
        "icon": "🧬",
        "page": "pages/sequence_analysis.py"
    },
    {
        "name": "Gene Discovery",
        "description": "Identify candidate open reading frames and investigate potential genes.",
        "icon": "🔬",
        "page": "pages/gene_discovery.py"
    },
    {
        "name": "Variant Analysis",
        "description": "Examine genetic variants, SNPs, insertions and deletions.",
        "icon": "🧩",
        "page": "pages/variant_analysis.py"
    },
    {
        "name": "Database Explorer",
        "description": "Retrieve biological records from established genomic databases.",
        "icon": "🗄️",
        "page": "pages/database_explorer.py"
    },
    {
        "name": "Functional Annotation",
        "description": "Investigate protein functions, domains and biological annotations.",
        "icon": "🧫",
        "page": "pages/functional_annotation.py"
    },
    {
        "name": "Crop Intelligence",
        "description": "Investigate crop traits and prioritise candidates using biological evidence.",
        "icon": "🌾",
        "page": "pages/crop_intelligence.py"
    }
]

st.markdown("### Available Research Tools")

for start in range(0, len(tools), 2):
    columns = st.columns(2)

    for column, tool in zip(columns, tools[start:start + 2]):
        with column:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="padding:10px 5px;">
                        <div style="font-size:30px;">{tool['icon']}</div>
                        <h3 style="margin:8px 0;">{tool['name']}</h3>
                        <p style="color:#718078;min-height:55px;">
                            {tool['description']}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(
                    "Open Tool →",
                    key=f"open_{tool['name']}",
                    type="primary",
                    use_container_width=True
                ):
                    st.switch_page(tool["page"])

st.divider()

st.markdown(
    """
    <div style="text-align:center;color:#718078;padding:15px;">
        GeneRescue AI · Crop Genomics & Bioinformatics Research
    </div>
    """,
    unsafe_allow_html=True
)
