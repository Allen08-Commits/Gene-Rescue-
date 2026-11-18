
"""GeneRescue AI welcome page."""

import streamlit as st


def render():
    st.markdown(
        """
        <div style="
            padding: 65px 35px;
            background: linear-gradient(120deg,#EAF2E9,#F7F9F6);
            border: 1px solid #DCE6DC;
            border-radius: 22px;
            text-align: center;
        ">
            <div style="font-size:55px;">🌱</div>
            <div class="brand-title">GeneRescue AI</div>
            <div class="brand-subtitle">
                Intelligent Genetic Rescue System for Crop Improvement
            </div>
            <p style="
                color:#526C5A;
                max-width:650px;
                margin:22px auto;
                line-height:1.8;
            ">
                An integrated bioinformatics research environment for
                sequence analysis, gene discovery, genetic variant
                investigation and crop-focused biological research.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    left, center, right = st.columns([1, 2, 1])

    with center:
        if st.button(
            "Enter Research Workspace  →",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["current_page"] = "home"
            st.rerun()

    st.write("")
    st.markdown("### Research capabilities")

    cols = st.columns(3)

    features = [
        ("🧬", "Sequence analysis", "Study DNA, RNA and protein sequences."),
        ("🔎", "Gene discovery", "Identify candidate open reading frames."),
        ("🧪", "Variant analysis", "Classify and summarize genetic variants."),
        ("🌐", "Database exploration", "Search established biological resources."),
        ("🔬", "Functional annotation", "Explore protein families and functions."),
        ("🌾", "Crop intelligence", "Investigate crop-related biological evidence."),
    ]

    for index, (icon, title, description) in enumerate(features):
        with cols[index % 3]:
            st.markdown(
                f"""
                <div class="tool-card">
                    <div style="font-size:27px">{icon}</div>
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write("")

    st.caption(
        "Research-support platform. Computational results require "
        "appropriate biological interpretation and validation."
    )
