
"""Variant Analysis research module."""

import pandas as pd
import plotly.express as px
import streamlit as st

from core.data_loader import load_vcf, load_table
from core.variant_analysis import analyze_variants, summarize_variants

from services.session_manager import create_research_session
from services.report_manager import generate_pdf_report


def render():
    st.title("🧪 Variant Analysis")
    st.write(
        "Upload genetic variant data to classify and summarize "
        "observed variant records."
    )

    uploaded = st.file_uploader(
        "Upload VCF, CSV or TSV",
        type=["vcf", "csv", "tsv", "txt"],
        key="variant_upload",
    )

    if uploaded is None:
        st.info("Upload your own variant dataset to begin.")
        return

    try:
        filename = uploaded.name.lower()

        if filename.endswith(".vcf"):
            raw_data = load_vcf(uploaded)
        else:
            raw_data = load_table(uploaded)

        st.success(f"Loaded {len(raw_data)} records.")

    except Exception as exc:
        st.error(f"Dataset loading failed: {exc}")
        return

    st.subheader("Uploaded data preview")
    st.dataframe(
        raw_data.head(20),
        use_container_width=True,
    )

    if st.button("Analyze variants", type="primary"):
        try:
            result = analyze_variants(raw_data)
            st.session_state["variant_analysis_result"] = result
        except Exception as exc:
            st.error(f"Variant analysis failed: {exc}")
            return

    result = st.session_state.get("variant_analysis_result")

    if result is None:
        return

    st.divider()
    st.subheader("Variant classification results")

    summary = summarize_variants(result)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total variants", summary["Total variants"])
    c2.metric("SNPs", summary["SNP count"])
    c3.metric("Insertions", summary["Insertion count"])
    c4.metric("Deletions", summary["Deletion count"])

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True,
    )

    counts = summary["Variant type counts"]

    if counts:
        chart_df = pd.DataFrame(
            list(counts.items()),
            columns=["Variant type", "Count"],
        )

        fig = px.bar(
            chart_df,
            x="Variant type",
            y="Count",
            title="Variant type distribution",
        )

        st.plotly_chart(fig, use_container_width=True)

    if st.button("Save variant analysis"):
        create_research_session(
            tool_name="Variant Analysis",
            session_title="Variant dataset analysis",
            input_summary=f"{len(raw_data)} input records",
            result_summary=(
                f"{summary['Total variants']} variants classified."
            ),
        )
        st.success("Variant analysis saved to session history.")

    pdf = generate_pdf_report(
        "GeneRescue AI - Variant Analysis",
        [
            {
                "heading": "Variant summary",
                "content": str(summary),
            },
            {
                "heading": "Normalized variant records",
                "dataframe": result,
            },
        ],
    )

    st.download_button(
        "Download variant analysis PDF",
        data=pdf,
        file_name="variant_analysis_report.pdf",
        mime="application/pdf",
    )

    st.caption(
        "This module classifies observed variants. It does not "
        "determine pathogenicity, clinical significance or "
        "functional impact."
    )
