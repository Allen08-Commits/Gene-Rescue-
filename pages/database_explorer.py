
"""External biological database explorer."""

import pandas as pd
import streamlit as st

from integrations import ncbi, ensembl_plants, uniprot, pubmed

from services.evidence_manager import save_evidence
from services.session_manager import create_research_session


def render():
    st.title("🌐 Database Explorer")
    st.write(
        "Search established biological databases and retrieve "
        "real external research records."
    )

    database = st.selectbox(
        "Select database",
        [
            "NCBI Gene",
            "NCBI Nucleotide",
            "NCBI Protein",
            "Ensembl Plants",
            "UniProt",
            "PubMed",
        ],
    )

    query = st.text_input(
        "Search term, gene symbol or accession",
        placeholder="Enter your search query...",
    )

    organism = ""

    if database == "NCBI Gene":
        organism = st.text_input(
            "Optional organism filter",
            placeholder="e.g. Oryza sativa",
        )

    limit = st.slider(
        "Maximum results",
        min_value=1,
        max_value=50,
        value=10,
    )

    if st.button("Search database", type="primary"):
        if not query.strip():
            st.warning("Enter a search term first.")
            return

        try:
            with st.spinner(f"Searching {database}..."):

                if database == "NCBI Gene":
                    results = ncbi.search_gene(
                        query,
                        organism=organism or None,
                        retmax=limit,
                    )

                elif database == "NCBI Nucleotide":
                    results = ncbi.search_nucleotide(
                        query,
                        retmax=limit,
                    )

                elif database == "NCBI Protein":
                    results = ncbi.search_protein(
                        query,
                        retmax=limit,
                    )

                elif database == "Ensembl Plants":
                    results = ensembl_plants.search_plant_genes(
                        query,
                    )

                elif database == "UniProt":
                    results = uniprot.search_proteins(
                        query,
                        size=limit,
                    )

                else:
                    results = pubmed.search_literature(
                        query,
                        limit=limit,
                    )

            st.session_state["database_search_results"] = results
            st.session_state["database_search_name"] = database

        except Exception as exc:
            st.error(f"Database search failed: {exc}")
            return

    results = st.session_state.get("database_search_results")

    if results is None:
        return

    if st.session_state.get("database_search_name") != database:
        return

    st.divider()
    st.subheader("Search results")

    if database.startswith("NCBI"):
        st.metric("Matching records", results.get("count", 0))

        identifiers = results.get("ids", [])

        if identifiers:
            st.dataframe(
                pd.DataFrame({"NCBI record ID": identifiers}),
                use_container_width=True,
                hide_index=True,
            )

            if st.button("Retrieve record summaries"):
                try:
                    summaries = ncbi.fetch_summaries(
                        identifiers,
                        database=results["database"],
                    )

                    st.session_state["ncbi_summaries"] = summaries

                except Exception as exc:
                    st.error(f"Summary retrieval failed: {exc}")

            summaries = st.session_state.get("ncbi_summaries")

            if summaries:
                st.json(summaries)

                selected_id = st.selectbox(
                    "Select record to save as evidence",
                    identifiers,
                )

                if st.button("Save selected NCBI evidence"):
                    save_evidence(
                        database="NCBI",
                        identifier=selected_id,
                        description="NCBI search result",
                        record_type="gene",
                    )
                    st.success("Evidence saved to this session.")

        else:
            st.info("No matching NCBI records were found.")

    elif database == "Ensembl Plants":
        if results:
            st.dataframe(
                pd.DataFrame(results),
                use_container_width=True,
                hide_index=True,
            )

            selected_id = st.selectbox(
                "Select Ensembl identifier",
                [item["id"] for item in results],
            )

            if st.button("Save Ensembl evidence"):
                save_evidence(
                    database="Ensembl Plants",
                    identifier=selected_id,
                    description="Ensembl Plants search result",
                    record_type="gene",
                )
                st.success("Evidence saved.")

        else:
            st.info("No matching Ensembl Plants records were found.")

    elif database == "UniProt":
        if results:
            display = pd.DataFrame([
                {
                    "Accession": item["accession"],
                    "Protein": item["protein_name"],
                    "Organism": item["organism"],
                    "Length": item["sequence_length"],
                    "Reviewed": item["reviewed"],
                }
                for item in results
            ])

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True,
            )

            selected = st.selectbox(
                "Select protein accession",
                [item["accession"] for item in results],
            )

            if st.button("Save UniProt evidence"):
                save_evidence(
                    database="UniProt",
                    identifier=selected,
                    description="UniProt protein search result",
                    record_type="protein",
                )
                st.success("Evidence saved.")

        else:
            st.info("No matching UniProt records were found.")

    else:
        if results:
            for article in results:
                with st.expander(
                    article.get("title") or article.get("pmid", "Article")
                ):
                    st.write(article.get("journal", ""))
                    st.write(article.get("year", ""))
                    st.write(article.get("abstract", ""))
                    st.link_button(
                        "Open PubMed article",
                        article["url"],
                    )

                    if st.button(
                        "Save this article",
                        key=f"save_pmid_{article['pmid']}",
                    ):
                        save_evidence(
                            database="PubMed",
                            identifier=article["pmid"],
                            description=article["title"],
                            source_url=article["url"],
                            record_type="article",
                        )
                        st.success("Article saved as evidence.")

        else:
            st.info("No matching publications were found.")

    if st.button("Save search activity"):
        create_research_session(
            tool_name="Database Explorer",
            session_title=f"{database} search",
            input_summary=query,
            result_summary="Database search completed.",
        )
        st.success("Search activity saved.")

    st.caption(
        "External database results depend on source availability "
        "and may change over time. Verify original records before "
        "using them in research conclusions."
    )
