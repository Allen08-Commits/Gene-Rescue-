
"""GeneRescue AI - Database Explorer."""

import pandas as pd
import streamlit as st

from integrations import (
    ncbi,
    ensembl_plants,
    uniprot,
    gramene,
    pubmed,
)

from services.session_manager import create_research_session


def render():
    st.title("Database Explorer")

    st.write(
        "Search public biological databases and retrieve "
        "gene, nucleotide, protein and literature information."
    )

    database = st.selectbox(
        "Select biological database",
        [
            "NCBI Gene",
            "NCBI Nucleotide",
            "Ensembl Plants",
            "UniProt",
            "PubMed",
            "Gramene",
        ],
    )

    query = st.text_input(
        "Search term, gene symbol or accession",
        placeholder="Enter your search query...",
    )

    organism = None

    if database == "NCBI Gene":
        organism = st.text_input(
            "Organism filter (optional)",
            placeholder="e.g. Oryza sativa",
        )

    species = "oryza_sativa"

    if database == "Ensembl Plants":
        species = st.text_input(
            "Ensembl species identifier",
            value="oryza_sativa",
            help="Use the species identifier recognized by Ensembl Plants.",
        )

    limit = st.number_input(
        "Maximum records",
        min_value=1,
        max_value=100,
        value=10,
    )

    if st.button(
        "Search Database",
        type="primary",
        disabled=not query.strip(),
    ):
        try:
            with st.spinner("Retrieving database records..."):

                if database == "NCBI Gene":
                    result = ncbi.search_gene(
                        query,
                        organism or None,
                        retmax=int(limit),
                    )

                elif database == "NCBI Nucleotide":
                    result = ncbi.search_nucleotide(
                        query,
                        retmax=int(limit),
                    )

                elif database == "Ensembl Plants":
                    result = ensembl_plants.search_plant_genes(
                        query,
                        species=species,
                    )

                elif database == "UniProt":
                    result = uniprot.search_proteins(
                        query,
                        size=int(limit),
                    )

                elif database == "PubMed":
                    result = pubmed.search_literature(
                        query,
                        limit=int(limit),
                    )

                else:
                    result = gramene.resource_links(query)

            st.session_state["last_database_result"] = result

            st.divider()
            st.subheader(f"{database} results")

            if not result:
                st.info("No matching records were returned.")

            elif isinstance(result, list):
                st.metric("Records returned", len(result))

                try:
                    st.dataframe(
                        pd.DataFrame(result),
                        use_container_width=True,
                        hide_index=True,
                    )
                except Exception:
                    st.json(result)

            else:
                st.json(result)

            create_research_session(
                tool_name="Database Explorer",
                session_title=f"{database} search",
                input_summary=query,
                result_summary=(
                    f"Search completed using {database}."
                ),
            )

            st.success("Database search completed.")

        except Exception as error:
            st.error(
                f"Database request failed: {error}"
            )

    st.divider()

    st.caption(
        "Database records are retrieved from external resources. "
        "Their availability and annotations depend on the provider."
    )
