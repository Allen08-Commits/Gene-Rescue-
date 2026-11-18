
"""Sequence Analysis research module."""

import pandas as pd
import plotly.express as px
import streamlit as st

from core.data_loader import (
    load_fasta,
    load_fastq,
    infer_sequence_type,
)
from core.sequence_analysis import (
    analyze_sequence,
    sliding_window_gc,
)
from core.sequence_quality import assess_sequence_quality

from services.session_manager import create_research_session
from services.project_manager import list_projects
from services.report_manager import generate_pdf_report


def render():
    st.title("🧬 Sequence Analysis")
    st.write(
        "Analyze DNA, RNA and protein sequences with "
        "composition, quality and statistical measurements."
    )

    tab1, tab2 = st.tabs([
        "Upload sequence",
        "Enter sequence",
    ])

    records = []

    with tab1:
        uploaded = st.file_uploader(
            "Upload FASTA or FASTQ",
            type=["fa", "fasta", "fna", "faa", "fq", "fastq"],
            key="sequence_upload",
        )

        if uploaded is not None:
            try:
                if uploaded.name.lower().endswith(
                    (".fq", ".fastq")
                ):
                    records = load_fastq(uploaded)
                else:
                    records = load_fasta(uploaded)

                st.success(
                    f"Loaded {len(records)} sequence record(s)."
                )

            except Exception as exc:
                st.error(f"Sequence loading failed: {exc}")

    with tab2:
        sequence_text = st.text_area(
            "Paste a DNA, RNA or protein sequence",
            height=150,
            placeholder="Enter your sequence here...",
        )

        sequence_type = st.selectbox(
            "Sequence type",
            ["Auto-detect", "DNA", "RNA", "Protein"],
        )

        if sequence_text.strip():
            cleaned = "".join(sequence_text.split()).upper()

            if sequence_type == "Auto-detect":
                detected = infer_sequence_type(cleaned)
            else:
                detected = sequence_type

            records = [{
                "id": "Pasted sequence",
                "description": "User-entered sequence",
                "sequence": cleaned,
                "sequence_type": detected,
                "length": len(cleaned),
            }]

    if not records:
        st.info("Upload a sequence file or enter a sequence to begin.")
        return

    labels = [
        f"{record['id']} ({record['sequence_type']})"
        for record in records
    ]

    selected = st.selectbox(
        "Select sequence",
        range(len(records)),
        format_func=lambda index: labels[index],
    )

    record = records[selected]
    sequence = record["sequence"]
    seq_type = record["sequence_type"]

    if seq_type == "unknown":
        st.error("The sequence type could not be determined.")
        return

    try:
        result = analyze_sequence(sequence, seq_type)
    except Exception as exc:
        st.error(f"Analysis failed: {exc}")
        return

    st.divider()
    st.subheader("Sequence statistics")

    c1, c2, c3 = st.columns(3)

    c1.metric("Sequence length", f"{len(sequence):,}")
    c2.metric("Sequence type", seq_type)
    c3.metric(
        "GC content",
        f"{result.get('GC content (%)', 0):.2f}%"
        if "GC content (%)" in result else "Not applicable",
    )

    st.dataframe(
        pd.DataFrame([
            {"Parameter": key, "Value": str(value)}
            for key, value in result.items()
            if key != "Sequence"
            and not isinstance(value, dict)
        ]),
        use_container_width=True,
        hide_index=True,
    )

    if seq_type in ("DNA", "RNA"):
        st.subheader("Nucleotide composition")

        composition = {
            base: sequence.count(base)
            for base in ("A", "C", "G", "T", "U", "N")
            if sequence.count(base) > 0
        }

        composition_df = pd.DataFrame(
            list(composition.items()),
            columns=["Nucleotide", "Count"],
        )

        fig = px.bar(
            composition_df,
            x="Nucleotide",
            y="Count",
            title="Nucleotide composition",
        )
        st.plotly_chart(fig, use_container_width=True)

        if len(sequence) >= 100:
            st.subheader("Sliding-window GC profile")

            window = st.number_input(
                "Window size",
                min_value=10,
                max_value=len(sequence),
                value=min(100, len(sequence)),
            )

            step = st.number_input(
                "Step size",
                min_value=1,
                max_value=len(sequence),
                value=25,
            )

            gc_records = sliding_window_gc(
                sequence,
                int(window),
                int(step),
            )

            gc_df = pd.DataFrame(gc_records)

            if not gc_df.empty:
                fig = px.line(
                    gc_df,
                    x="Start",
                    y="GC content (%)",
                    title="GC content across sequence",
                )
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

        quality_scores = record.get("phred_quality")

        quality = assess_sequence_quality(
            sequence,
            quality_scores,
        )

        st.subheader("Sequence quality assessment")

        st.dataframe(
            pd.DataFrame([
                {"Metric": key, "Value": str(value)}
                for key, value in quality.items()
            ]),
            use_container_width=True,
            hide_index=True,
        )

        if quality_scores is None:
            st.info(
                "This sequence has no FASTQ Phred scores. "
                "The displayed values are composition screening, "
                "not sequencing quality scores."
            )

    st.subheader("Research project association")

    projects = list_projects()

    project_options = ["No project"] + [
        project["project_name"]
        for project in projects
    ]

    project_choice = st.selectbox(
        "Associate this analysis with a project",
        project_options,
    )

    project_id = None

    if project_choice != "No project":
        project_id = next(
            p["project_id"]
            for p in projects
            if p["project_name"] == project_choice
        )

    if st.button("Save analysis to research history"):
        create_research_session(
            tool_name="Sequence Analysis",
            session_title=f"Analysis of {record['id']}",
            input_summary=(
                f"Sequence length: {len(sequence)}; "
                f"Type: {seq_type}"
            ),
            result_summary="Sequence statistics calculated.",
            project_id=project_id,
        )
        st.success("Analysis saved to the current session.")

    report_sections = [
        {
            "heading": "Sequence information",
            "content": (
                f"Record: {record['id']}\n"
                f"Type: {seq_type}\n"
                f"Length: {len(sequence)}"
            ),
        },
        {
            "heading": "Sequence statistics",
            "dataframe": pd.DataFrame([
                {"Parameter": key, "Value": str(value)}
                for key, value in result.items()
                if key != "Sequence"
                and not isinstance(value, dict)
            ]),
        },
    ]

    pdf = generate_pdf_report(
        "GeneRescue AI - Sequence Analysis",
        report_sections,
    )

    st.download_button(
        "Download sequence analysis PDF",
        data=pdf,
        file_name="sequence_analysis_report.pdf",
        mime="application/pdf",
    )
