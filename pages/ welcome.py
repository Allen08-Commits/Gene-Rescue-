
import streamlit as st

st.set_page_config(
    page_title="GeneRescue AI",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 GeneRescue AI")
st.subheader("Intelligent Genetic Rescue System for Crop Improvement")

st.write(
    "An integrated research platform for sequence analysis, "
    "gene discovery, variant analysis and crop intelligence."
)

st.write("Explore bioinformatics tools and biological databases.")

if st.button("Enter Research Workspace", type="primary"):
    st.switch_page("pages/home.py")
