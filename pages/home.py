
"""GeneRescue AI - Main research workspace."""

import streamlit as st


st.markdown(
    """
    <div class="brand-title">GeneRescue AI</div>
    <div class="brand-subtitle">
        Intelligent Genetic Rescue System for Crop Improvement
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

st.markdown(
    """
    <div class="page-heading">Research Workspace</div>
    <div class="page-description">
        Select a bioinformatics tool to begin your investigation.
        Each module can be used independently.
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

TOOLS = [
    {
        "name": "Sequence Analysis",
        "description": (
            "Analyze DNA, RNA and protein sequences, "
            "calculate sequence properties and assess quality."
        ),
        "icon": "🧬",
        "page": "pages/sequence_analysis.py",
    },
    {
        "name": "Gene Discovery",
        "description": (
            "Identify candidate open reading frames and "
            "investigate gene-related sequence features."
        ),
        "icon": "🔬",
        "page": "pages/gene_discovery.py",
    },
    {
        "name": "Variant Analysis",
        "description": (
            "Inspect genetic variants, classify variant types "
            "and examine their annotations."
        ),
        "icon": "🧪",
        "page": "pages/variant_analysis.py",
    },
    {
        "name": "Database Explorer",
        "description": (
            "Search biological databases and retrieve "
            "gene, protein and literature records."
        ),
        "icon": "🌐",
        "page": "pages/database_explorer.py",
    },
    {
        "name": "Functional Annotation",
        "description": (
            "Investigate protein domains, biological functions "
            "and cross-database annotations."
        ),
        "icon": "🧫",
        "page": "pages/functional_annotation.py",
    },
    {
        "name": "Crop Intelligence",
        "description": (
            "Investigate crop-associated genes and evaluate "
            "evidence-supported improvement hypotheses."
        ),
        "icon": "🌾",
        "page": "pages/crop_intelligence.py",
    },
]

for row_start in range(0, len(TOOLS), 3):
    columns = st.columns(3, gap="large")

    for column, tool in zip(
        columns,
        TOOLS[row_start:row_start + 3],
    ):
        with column:
            st.markdown(
                f"""
                <div class="tool-card">
                    <div style="font-size:30px;">
                        {tool["icon"]}
                    </div>
                    <h3>{tool["name"]}</h3>
                    <p>{tool["description"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                f"Open {tool['name']}",
                key=f"open_{tool['name']}",
                use_container_width=True,
            ):
                st.switch_page(tool["page"])

            st.write("")

st.divider()

st.caption(
    "Research outputs are computational findings. "
    "Predictions require independent biological validation."
)
