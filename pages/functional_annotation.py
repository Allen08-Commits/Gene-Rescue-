
"""GeneRescue AI - Functional Annotation."""

import pandas as pd
import streamlit as st

from integrations import uniprot, interpro

from services.session_manager import create_research_session


def render():
    st.title("Functional Annotation")

    st.write(
        "Investigate protein identity, organism information, "
        "protein families and conserved functional domains."
    )

    accession = st.text_input(
        "UniProt accession or protein search term",
        placeholder="Enter a UniProt accession or protein name...",
    )

    if st.button(
        "Retrieve Functional Annotation",
        type="primary",
        disabled=not accession.strip(),
    ):
        try:
            with st.spinner("Searching UniProt..."):
                proteins = uniprot.search_proteins(
                    accession,
                    size=5,
                )

            st.divider()
            st.subheader("UniProt protein records")

            if not proteins:
                st.info(
                    "No UniProt records were returned. "
                    "Check the accession or try another search term."
                )
                return

            st.dataframe(
                pd.DataFrame(proteins),
                use_container_width=True,
                hide_index=True,
            )

            selected_accession = st.selectbox(
                "Select protein accession for InterPro lookup",
                [
                    item["accession"]
                    for item in proteins
                    if item.get("accession")
                ],
            )

            if selected_accession:
                with st.spinner("Retrieving InterPro annotations..."):
                    annotation = (
                        interpro.search_protein_accession(
                            selected_accession
                        )
                    )

                st.divider()
                st.subheader("InterPro domain and family results")

                if annotation:
                    st.json(annotation)
                else:
                    st.info(
                        "No InterPro matches were returned."
                    )

            st.session_state["last_functional_annotation"] = {
                "uniprot": proteins,
                "interpro": annotation if selected_accession else None,
            }

            create_research_session(
                tool_name="Functional Annotation",
                session_title=(
                    f"Protein annotation: {accession}"
                ),
                input_summary=accession,
                result_summary=(
                    f"{len(proteins)} UniProt records retrieved."
                ),
            )

            st.success("Functional annotation retrieval completed.")

        except Exception as error:
            st.error(
                f"Functional annotation failed: {error}"
            )

    st.caption(
        "Retrieved protein annotations and domain matches are "
        "database evidence, not experimental confirmation of function."
    )
