
"""GeneRescue AI - Variant Analysis."""

import pandas as pd
import streamlit as st

from core.data_loader import load_vcf, load_table
from core.variant_analysis import analyze_variants
from services.session_manager import create_research_session


def render():
    st.title("Variant Analysis")

    st.write(
        "Perform descriptive classification of genetic variants "
        "from user-provided VCF, CSV or TSV files."
    )

    st.warning(
        "Variant classification alone does not establish pathogenicity, "
        "functional impact or crop-trait association."
    )

    uploaded_file = st.file_uploader(
        "Upload variant dataset",
        type=["vcf", "csv", "tsv", "txt"],
        key="variant_upload",
    )

    if not uploaded_file:
        st.info(
            "Upload your own variant file to begin. "
            "Required columns for tabular files: REF and ALT."
        )
        return

    try:
        filename = uploaded_file.name.lower()

        if filename.endswith(".vcf"):
            data = load_vcf(uploaded_file)
        else:
            data = load_table(uploaded_file)

        st.subheader("Uploaded dataset")

        st.metric(
            "Input variant records",
            len(data),
        )

        st.dataframe(
            data.head(20),
            use_container_width=True,
            hide_index=True,
        )

        if st.button(
            "Classify Variants",
            type="primary",
        ):
            results = analyze_variants(data)

            st.session_state["last_variant_results"] = results

            st.divider()
            st.subheader("Variant classification results")

            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True,
            )

            st.subheader("Variant type distribution")

            counts = (
                results["Variant_Type"]
                .value_counts()
                .rename_axis("Variant type")
                .reset_index(name="Count")
            )

            st.bar_chart(
                counts.set_index("Variant type")
            )

            col1, col2, col3 = st.columns(3)

            col1.metric("Total variants", len(results))
            col2.metric(
                "SNPs",
                int((results["Variant_Type"] == "SNP").sum()),
            )
            col3.metric(
                "Insertions",
                int(
                    (results["Variant_Type"] == "Insertion").sum()
                ),
            )

            st.download_button(
                "Download classified variants",
                data=results.to_csv(index=False),
                file_name="variant_classification.csv",
                mime="text/csv",
            )

            create_research_session(
                tool_name="Variant Analysis",
                session_title="Variant classification",
                input_summary=f"Input records: {len(data)}",
                result_summary=(
                    f"Classified {len(results)} variant records."
                ),
            )

            st.success("Variant classification completed.")

    except Exception as error:
        st.error(f"Variant analysis failed: {error}")
