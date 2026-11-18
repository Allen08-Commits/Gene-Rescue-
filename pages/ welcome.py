
import streamlit as st

st.markdown(
    """
    <div style="text-align:center; padding:90px 15px 35px;">
        <div style="font-size:65px;">🌱</div>
        <div class="brand-title">GeneRescue AI</div>
        <div class="brand-subtitle">
            INTELLIGENT GENETIC RESEARCH FOR CROP IMPROVEMENT
        </div>
        <br>
        <p style="max-width:680px;margin:auto;color:#718078;font-size:17px;line-height:1.8;">
            An integrated bioinformatics research platform for sequence
            investigation, gene discovery, genetic variant analysis and
            evidence-based crop improvement research.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

left, center, right = st.columns([1, 2, 1])

with center:
    st.markdown(
        """
        <div style="text-align:center;padding:15px;">
            <h3>Explore biological data. Investigate genetic evidence.</h3>
            <p style="color:#718078;">
                Access computational research tools and established
                biological databases in one workspace.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Get Started", type="primary", use_container_width=True):
        st.switch_page("pages/login.py")

    st.markdown(
        """
        <div style="text-align:center;color:#718078;font-size:13px;">
            Already have an account? Sign in to continue.
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Login", use_container_width=True):
        st.switch_page("pages/login.py")

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;padding:15px;color:#718078;">
        <b>GeneRescue AI</b><br>
        Computational research support for crop genomics and bioinformatics.
    </div>
    """,
    unsafe_allow_html=True
)
