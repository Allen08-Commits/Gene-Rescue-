
"""Functional Annotation research module."""

import pandas as pd
import streamlit as st

from integrations import uniprot, interpro

from services.evidence_manager import save_evidence
from services.session_manager import create_research_session
from services.report_manager import generate_pdf_report


def render():
    st.title("🔬 Functional Annotation")
    st.write(
        "Retrieve protein information and investigate "
        "protein family and domain annotations."
    )

    accession = st.text_input(
        "UniProt protein accession",
        placeholder="Enter an accession, e.g. P04637",
    )

    if not accession.strip():
        st.info("Enter a protein accession to begin.")
        return

    if st.button("Retrieve protein annotation", type="primary"):
        try:
            with st.spinner("Retrieving UniProt and InterPro records..."):
                protein = uniprot.get_protein_entry(accession)
                protein_fasta = uniprot.get_protein_fasta(accession)
                domain_data = interpro.search_protein_accession(
                    accession
                )

            st.session_state["annotation_protein"] = protein
            st.session_state["annotation_fasta"] = protein_fasta
            st.session_state["annotation_domains"] = domain_data
            st.session_state["annotation_accession"] = accession

        except Exception as exc:
            st.error(f"Annotation retrieval failed: {exc}")
            return

    if st.session_state.get("annotation_accession") != accession:
        return

    protein = st.session_state.get("annotation_protein")
    fasta = st.session_state.get("annotation_fasta")
    domains = st.session_state.get("annotation_domains")

    if not protein or not domains:
        return

    record = protein["record"]
    sequence = fasta["fasta"]

    st.divider()
    st.subheader("UniProt protein record")

    description = record.get("proteinDescription", {})
    recommended = description.get("recommendedName", {})
    name = recommended.get("fullName", {}).get("value", "Not available")

    organism = record.get("organism", {}).get(
        "scientificName",
        "Not available",
    )

    sequence_info = record.get("sequence", {})

    c1, c2, c3 = st.columns(3)
    c1.metric("Protein", accession)
    c2.metric("Sequence length", sequence_info.get("length", "N/A"))
    c3.metric("Organism", organism)

    st.write("**Protein name:**", name)

    st.subheader("Protein sequence")
    st.code(sequence, language="text")

    st.subheader("InterPro matches")

    matches = domains.get("matches", [])

    if matches:
        match_df = pd.DataFrame([
            {
                "InterPro accession": item["accession"],
                "Name": item["name"],
                "Type": item["type"],
                "Source database": item["source_database"],
            }
            for item in matches
        ])

        st.metric("Domain/family matches", len(matches))

        st.dataframe(
            match_df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info(
            "No InterPro matches were returned for this accession."
        )

    if st.button("Save protein evidence"):
        save_evidence(
            database="UniProt",
            identifier=accession,
            description=name,
            record_type="protein",
        )

        st.success("Protein evidence saved.")

    report_sections = [
        {
            "heading": "Protein information",
            "content": (
                f"Accession: {accession}\n"
                f"Protein: {name}\n"
                f"Organism: {organism}\n"
                f"Length: {sequence_info.get('length', 'N/A')}"
            ),
        },
    ]

    if matches:
        report_sections.append({
            "heading": "InterPro matches",
            "dataframe": match_df,
        })

    pdf = generate_pdf_report(
        "GeneRescue AI - Functional Annotation",
        report_sections,
    )

    st.download_button(
        "Download annotation report",
        data=pdf,
        file_name="functional_annotation_report.pdf",
        mime="application/pdf",
    )

    st.caption(
        "Database annotations describe reported or computationally "
        "predicted protein features. They are not experimental "
        "confirmation of biological function."
    )
