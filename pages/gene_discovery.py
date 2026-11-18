
"""GeneRescue AI - Gene Discovery."""

import pandas as pd
import streamlit as st

from core.data_loader import load_fasta
from core.gene_identification import identify_orfs
from services.session_manager import create_research_session


def render():
    st.title("Gene Discovery")

    st.write(
        "Identify candidate open reading frames (ORFs) from "
        "user-provided DNA sequences."
    )

    st.warning(
        "An ORF is a computational candidate, not a confirmed "
        "gene. Experimental or independent annotation evidence "
        "is required for validation."
    )

    uploaded_file = st.file_uploader(
        "Upload DNA FASTA file",
        type=["fa", "fasta", "fna"],
        key="gene_fasta",
    )

    sequence = ""
    sequence_name = "User sequence"

    if uploaded_file:
        try:
            records = load_fasta(uploaded_file)

            selected = st.selectbox(
                "Select sequence record",
                range(len(records)),
                format_func=lambda i: records[i]["id"],
            )

            sequence = records[selected]["sequence"]
            sequence_name = records[selected]["id"]

        except Exception as error:
            st.error(f"FASTA processing failed: {error}")

    else:
        sequence = st.text_area(
            "Or paste a DNA sequence",
            height=170,
            placeholder="Paste your DNA sequence here...",
            key="gene_sequence",
        )

    minimum_length = st.number_input(
        "Minimum ORF length (amino acids)",
        min_value=1,
        max_value=5000,
        value=30,
        step=1,
    )

    if st.button(
        "Identify Candidate ORFs",
        type="primary",
        disabled=not sequence.strip(),
    ):
        try:
            results = identify_orfs(
                sequence,
                min_amino_acids=int(minimum_length),
            )

            st.session_state["last_orf_results"] = results

            st.divider()
            st.subheader("ORF identification results")

            st.metric(
                "Candidate ORFs identified",
                len(results),
            )

            if results:
                result_df = pd.DataFrame(results)

                st.dataframe(
                    result_df,
                    use_container_width=True,
                    hide_index=True,
                )

                csv_data = result_df.to_csv(index=False)

                st.download_button(
                    "Download complete ORF results",
                    data=csv_data,
                    file_name="candidate_orfs.csv",
                    mime="text/csv",
                )

                st.subheader("Candidate protein sequences")

                for record in results:
                    with st.expander(record["ORF_ID"]):
                        st.write(
                            f"Strand: {record['Strand']}"
                        )
                        st.write(
                            f"Reading frame: {record['Frame']}"
                        )
                        st.write(
                            f"Coordinates: {record['Start']} - "
                            f"{record['End']}"
                        )
                        st.code(
                            record["Protein_Sequence"],
                            language="text",
                        )

            else:
                st.info(
                    "No ORFs satisfied the selected minimum length."
                )

            create_research_session(
                tool_name="Gene Discovery",
                session_title=f"ORF analysis: {sequence_name}",
                input_summary=(
                    f"Minimum ORF length: {minimum_length} amino acids"
                ),
                result_summary=(
                    f"{len(results)} candidate ORFs identified."
                ),
            )

            st.success("ORF analysis completed.")

        except Exception as error:
            st.error(f"Gene discovery failed: {error}")
