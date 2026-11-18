
"""GeneRescue AI - Welcome page."""

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
    <div style="
        padding: 65px 35px;
        background: linear-gradient(135deg, #edf4ed, #f8faf7);
        border-radius: 18px;
        border: 1px solid #dce8dc;
        text-align: center;
    ">
        <div style="
            color: #397a58;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 2px;
        ">
            BIOINFORMATICS RESEARCH PLATFORM
        </div>

        <h1 style="
            color: #20372b;
            font-size: 42px;
            margin-top: 22px;
        ">
            Explore genes.<br>Understand biology.
        </h1>

        <p style="
            color: #627568;
            font-size: 17px;
            max-width: 680px;
            margin: 20px auto;
        ">
            Analyze biological sequences, investigate genes, explore
            genetic variants, retrieve database evidence and evaluate
            crop improvement opportunities using bioinformatics tools.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
st.write("")

left, center, right = st.columns([1, 1.4, 1])

with center:
    if st.button(
        "Enter Research Workspace",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/home.py")

st.write("")
st.markdown(
    """
    <div style="text-align:center;color:#829087;font-size:12px;">
        GeneRescue AI · Computational Biology · Crop Research
    </div>
    """,
    unsafe_allow_html=True,
)
