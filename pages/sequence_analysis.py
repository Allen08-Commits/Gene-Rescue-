
"""GeneRescue AI - Sequence Analysis."""

import json
import pandas as pd
import streamlit as st

from core.data_loader import load_fasta
from core.sequence_analysis import analyze_sequence
from core.sequence_quality import composition_screen
from services.session_manager import create_research_session


def render():
    st.title("Sequence Analysis")
    st.write(
        "Analyze DNA, RNA and protein sequences using "
        "sequence composition and statistical methods."
    )

    st.subheader("Sequence input")

    input_method = st.radio(
        "Choose input method",
        ["Upload FASTA", "Paste sequence"],
        horizontal=True,
    )

    sequence = ""
    sequence_name = "User sequence"

    if input_method == "Upload FASTA":
        uploaded_file = st.file_uploader(
            "Upload your FASTA file",
            type=["fa", "fasta", "fna", "faa"],
            key="sequence_upload",
        )

        if uploaded_file:
            try:
                records = load_fasta(uploaded_file)

                selected = st.selectbox(
                    "Select sequence record",
                    range(len(records)),
                    format_func=lambda i: (
                        f"{records[i]['id']} "
                        f"({len(records[i]['sequence'])} characters)"
                    ),
                )

                sequence = records[selected]["sequence"]
                sequence_name = records[selected]["id"]

            except Exception as error:
                st.error(f"FASTA processing failed: {error}")

    else:
        sequence = st.text_area(
            "Paste biological sequence",
            height=180,
            placeholder="Paste your DNA, RNA or protein sequence here...",
        )

    sequence_type = st.selectbox(
        "Sequence type",
        ["Auto-detect", "DNA", "RNA", "Protein"],
        help=(
            "Choose the correct type manually when a sequence contains "
            "only A, C, G and T, since such a sequence can be ambiguous."
        ),
    )

    if st.button(
        "Analyze Sequence",
        type="primary",
        disabled=not sequence.strip(),
    ):
        try:
            result = analyze_sequence(
                sequence,
                sequence_type=sequence_type,
            )

            quality = composition_screen(sequence)

            st.session_state["last_sequence"] = sequence
            st.session_state["last_sequence_result"] = result
            st.session_state["last_sequence_quality"] = quality

            st.divider()
            st.subheader(f"Analysis Results: {sequence_name}")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Sequence length",
                result["Length"],
            )

            col2.metric(
                "Sequence type",
                result["Sequence type"],
            )

            col3.metric(
                "Ambiguous symbols",
                result["Ambiguous symbols"],
            )

            st.subheader("Sequence statistics")
            st.json(result)

            st.subheader("Composition screening")
            st.json(quality)

            report = {
                "sequence_name": sequence_name,
                "statistics": result,
                "composition_screen": quality,
            }

            st.download_button(
                "Download analysis results",
                data=json.dumps(report, indent=4),
                file_name="sequence_analysis.json",
                mime="application/json",
            )

            create_research_session(
                tool_name="Sequence Analysis",
                session_title=f"Analysis of {sequence_name}",
                input_summary=(
                    f"Sequence type: {result['Sequence type']}; "
                    f"Length: {result['Length']}"
                ),
                result_summary=(
                    f"Analysis completed for {sequence_name}"
                ),
            )

            st.success("Sequence analysis completed.")

        except Exception as error:
            st.error(f"Sequence analysis failed: {error}")

    st.caption(
        "Note: Composition screening is not a Phred-based "
        "sequencing quality assessment."
    )
