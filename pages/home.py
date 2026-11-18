
"""GeneRescue AI research workspace."""

import streamlit as st


TOOLS = [
    {
        "key": "sequence_analysis",
        "number": "01",
        "icon": "🧬",
        "name": "Sequence Analysis",
        "description": (
            "Analyze DNA, RNA and protein sequences, "
            "composition, GC content and sequence quality."
        ),
    },
    {
        "key": "gene_discovery",
        "number": "02",
        "icon": "🔎",
        "name": "Gene Discovery",
        "description": (
            "Identify candidate open reading frames "
            "across six reading frames."
        ),
    },
    {
        "key": "variant_analysis",
        "number": "03",
        "icon": "🧪",
        "name": "Variant Analysis",
        "description": (
            "Explore VCF records and classify genetic variants."
        ),
    },
    {
        "key": "database_explorer",
        "number": "04",
        "icon": "🌐",
        "name": "Database Explorer",
        "description": (
            "Search NCBI, Ensembl Plants, UniProt and PubMed."
        ),
    },
    {
        "key": "functional_annotation",
        "number": "05",
        "icon": "🔬",
        "name": "Functional Annotation",
        "description": (
            "Investigate protein records, domains "
            "and functional annotations."
        ),
    },
    {
        "key": "crop_intelligence",
        "number": "06",
        "icon": "🌾",
        "name": "Crop Intelligence",
        "description": (
            "Explore plant genomics resources and "
            "crop-related scientific literature."
        ),
    },
]


def render():
    st.markdown(
        '<div class="page-heading">Research Workspace</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-description">'
        'Select an independent research module to begin your analysis.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    for row_start in range(0, len(TOOLS), 2):
        columns = st.columns(2, gap="large")

        for column, tool in zip(
            columns,
            TOOLS[row_start:row_start + 2],
        ):
            with column:
                st.markdown(
                    f"""
                    <div class="tool-card">
                        <div style="
                            display:flex;
                            justify-content:space-between;
                            align-items:center;
                        ">
                            <span style="font-size:30px">
                                {tool["icon"]}
                            </span>
                            <span style="
                                color:#78917E;
                                font-size:12px;
                                font-weight:700;
                            ">
                                MODULE {tool["number"]}
                            </span>
                        </div>
                        <h3>{tool["name"]}</h3>
                        <p>{tool["description"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(
                    f"Open {tool['name']} →",
                    key=f"open_{tool['key']}",
                    use_container_width=True,
                ):
                    st.session_state["current_page"] = tool["key"]
                    st.rerun()

                st.write("")

    st.divider()

    projects = st.session_state.get("research_projects", [])
    evidence = st.session_state.get("research_evidence", [])
    history = st.session_state.get("research_history", [])

    st.markdown("### Current session")

    c1, c2, c3 = st.columns(3)

    c1.metric("Research projects", len(projects))
    c2.metric("Saved evidence", len(evidence))
    c3.metric("Research activities", len(history))

    st.caption(
        "These records are temporary and remain available only "
        "during the active application session."
    )

    if st.button("Return to Welcome Page"):
        st.session_state["current_page"] = "welcome"
        st.rerun()
