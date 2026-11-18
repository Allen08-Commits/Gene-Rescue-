
"""Gene Discovery research module."""

import pandas as pd
import streamlit as st

from core.data_loader import load_fasta, infer_sequence_type
from core.gene_identification import identify_orfs

from services.session_manager import create_research_session
from services.report_manager import generate_pdf_report


def render():
    st.title("🔎 Gene Discovery")
    st.write(
        "Identify candidate open reading frames from DNA sequences "
        "across the forward and reverse strands."
    )

    tab1, tab2 = st.tabs([
        "Upload FASTA",
        "Paste DNA sequence",
    ])

    sequence = ""
    record_id = ""

    with tab1:
        uploaded = st.file_uploader(
            "Upload DNA FASTA",
            type=["fa", "fasta", "fna"],
            key="gene_fasta",
        )

        records = []

        if uploaded:
            try:
                records = load_fasta(uploaded)
            except Exception as exc:
                st.error(f"FASTA loading failed: {exc}")

        if records:
            index = st.selectbox(
                "Choose sequence",
                range(len(records)),
                format_func=lambda i: records[i]["id"],
            )

            sequence = records[index]["sequence"]
            record_id = records[index]["id"]

    with tab2:
        pasted = st.text_area(
            "Paste DNA sequence",
            height=150,
            placeholder="ATG...",
        )

        if pasted.strip():
            sequence = "".join(pasted.split()).upper()
            record_id = "Pasted DNA"

    if not sequence:
        st.info("Upload a FASTA file or paste a DNA sequence.")
        return

    if infer_sequence_type(sequence) != "DNA":
        st.error("Gene discovery requires a DNA sequence.")
        return

    min_length = st.number_input(
        "Minimum ORF length (amino acids)",
        min_value=1,
        max_value=10000,
        value=30,
    )

    include_nested = st.checkbox(
        "Include nested start codons",
        value=False,
    )

    if st.button("Identify candidate ORFs", type="primary"):
        try:
            orfs = identify_orfs(
                sequence,
                min_amino_acids=int(min_length),
                nested=include_nested,
            )

            st.session_state["last_orf_results"] = orfs
            st.session_state["last_orf_record"] = record_id

        except Exception as exc:
            st.error(f"ORF analysis failed: {exc}")
            return

    if "last_orf_results" not in st.session_state:
        return

    if st.session_state.get("last_orf_record") != record_id:
        return

    orfs = st.session_state["last_orf_results"]

    st.divider()
    st.subheader("Candidate ORF results")

    st.metric("Candidate ORFs found", len(orfs))

    if not orfs:
        st.warning(
            "No candidate ORFs matched the selected minimum length."
        )
        return

    dataframe = pd.DataFrame(orfs)

    st.dataframe(
        dataframe.drop(
            columns=["Coding_Sequence", "Protein_Sequence"],
            errors="ignore",
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Candidate protein sequences")

    selected_orf = st.selectbox(
        "Select an ORF",
        range(len(orfs)),
        format_func=lambda i: orfs[i]["ORF_ID"],
    )

    selected_record = orfs[selected_orf]

    st.code(
        f">{selected_record['ORF_ID']}\n"
        f"{selected_record['Protein_Sequence']}",
        language="text",
    )

    if st.button("Save ORF analysis"):
        create_research_session(
            tool_name="Gene Discovery",
            session_title=f"ORF analysis: {record_id}",
            input_summary=f"Input DNA length: {len(sequence)}",
            result_summary=(
                f"{len(orfs)} candidate ORFs identified."
            ),
        )
        st.success("ORF analysis saved to research history.")

    pdf = generate_pdf_report(
        "GeneRescue AI - Gene Discovery",
        [
            {
                "heading": "Input sequence",
                "content": (
                    f"Record: {record_id}\n"
                    f"Sequence length: {len(sequence)}"
                ),
            },
            {
                "heading": "Candidate ORFs",
                "dataframe": dataframe.drop(
                    columns=["Coding_Sequence", "Protein_Sequence"],
                    errors="ignore",
                ),
            },
        ],
    )

    st.download_button(
        "Download ORF report",
        data=pdf,
        file_name="gene_discovery_report.pdf",
        mime="application/pdf",
    )

    st.caption(
        "ORFs are computational candidates. They are not "
        "confirmed genes or evidence of expression."
    )
