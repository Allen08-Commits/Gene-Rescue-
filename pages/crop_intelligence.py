
"""Crop Intelligence research module."""

import streamlit as st
import pandas as pd

from integrations import gramene, ensembl_plants, pubmed

from services.evidence_manager import save_evidence
from services.session_manager import create_research_session
from services.report_manager import generate_pdf_report


def render():
    st.title("🌾 Crop Intelligence")
    st.write(
        "Explore crop-related genomics resources, plant gene records "
        "and scientific literature."
    )

    tab1, tab2 = st.tabs([
        "Plant resource explorer",
        "Scientific literature",
    ])

    with tab1:
        st.subheader("Plant genomics search")

        query = st.text_input(
            "Crop, organism, gene symbol or identifier",
            placeholder="e.g. rice, drought tolerance, Os01g...",
            key="crop_query",
        )

        species = st.selectbox(
            "Ensembl Plants species",
            [
                "oryza_sativa",
                "arabidopsis_thaliana",
                "zea_mays",
                "sorghum_bicolor",
                "triticum_aestivum",
                "glycine_max",
            ],
        )

        if st.button("Explore plant resources", type="primary"):
            if not query.strip():
                st.warning("Enter a crop or gene search term.")
            else:
                try:
                    with st.spinner("Searching plant resources..."):
                        links = gramene.resource_links(query)
                        genes = ensembl_plants.search_plant_genes(
                            query,
                            species=species,
                        )

                    st.session_state["crop_resource_links"] = links
                    st.session_state["crop_gene_results"] = genes
                    st.session_state["crop_active_query"] = query

                except Exception as exc:
                    st.error(f"Plant resource search failed: {exc}")

        if st.session_state.get("crop_active_query") == query and query:
            links = st.session_state.get("crop_resource_links", [])
            genes = st.session_state.get("crop_gene_results", [])

            st.subheader("External plant research resources")

            for item in links:
                st.markdown(
                    f"**[{item['name']}]({item['url']})**"
                )
                st.caption(item["note"])

            st.subheader("Ensembl Plants gene matches")

            if genes:
                st.dataframe(
                    pd.DataFrame(genes),
                    use_container_width=True,
                    hide_index=True,
                )

                selected = st.selectbox(
                    "Select gene identifier to save",
                    [item["id"] for item in genes],
                    key="crop_selected_gene",
                )

                if st.button("Save plant gene evidence"):
                    save_evidence(
                        database="Ensembl Plants",
                        identifier=selected,
                        description=(
                            f"Plant gene search for {query}"
                        ),
                        record_type="gene",
                    )
                    st.success("Plant gene evidence saved.")

            else:
                st.info(
                    "No Ensembl Plants gene matches were returned. "
                    "You can still explore the external resources."
                )

    with tab2:
        st.subheader("Crop-related scientific literature")

        literature_query = st.text_input(
            "Enter a scientific literature query",
            placeholder=(
                "e.g. rice drought tolerance gene expression"
            ),
        )

        limit = st.slider(
            "Maximum publications",
            min_value=1,
            max_value=30,
            value=10,
        )

        if st.button("Search scientific literature"):
            if not literature_query.strip():
                st.warning("Enter a literature query.")
            else:
                try:
                    with st.spinner("Searching PubMed..."):
                        articles = pubmed.search_literature(
                            literature_query,
                            limit=limit,
                        )

                    st.session_state["crop_literature"] = articles
                    st.session_state["crop_literature_query"] = literature_query

                except Exception as exc:
                    st.error(f"Literature search failed: {exc}")

        articles = st.session_state.get("crop_literature", [])

        if (
            articles
            and st.session_state.get("crop_literature_query")
            == literature_query
        ):
            st.metric("Publications found", len(articles))

            for article in articles:
                with st.expander(
                    article.get("title") or article.get("pmid")
                ):
                    st.write(
                        f"**Journal:** {article.get('journal', '')}"
                    )
                    st.write(
                        f"**Year:** {article.get('year', '')}"
                    )
                    st.write(article.get("abstract", ""))

                    st.link_button(
                        "Read PubMed record",
                        article["url"],
                    )

                    if st.button(
                        "Save publication evidence",
                        key=f"crop_save_{article['pmid']}",
                    ):
                        save_evidence(
                            database="PubMed",
                            identifier=article["pmid"],
                            description=article["title"],
                            source_url=article["url"],
                            record_type="article",
                        )
                        st.success("Publication evidence saved.")

            pdf = generate_pdf_report(
                "GeneRescue AI - Crop Literature Report",
                [
                    {
                        "heading": "Literature search",
                        "content": literature_query,
                    },
                    {
                        "heading": "Publication records",
                        "dataframe": pd.DataFrame([
                            {
                                "PMID": a["pmid"],
                                "Title": a["title"],
                                "Journal": a["journal"],
                                "Year": a["year"],
                                "URL": a["url"],
                            }
                            for a in articles
                        ]),
                    },
                ],
            )

            st.download_button(
                "Download literature report",
                data=pdf,
                file_name="crop_literature_report.pdf",
                mime="application/pdf",
            )

    st.divider()

    if st.button("Save crop research activity"):
        create_research_session(
            tool_name="Crop Intelligence",
            session_title="Crop intelligence research",
            input_summary="Plant resource and literature exploration",
            result_summary="Research exploration completed.",
        )
        st.success("Research activity saved to this session.")

    st.caption(
        "Database matches and publications provide research leads. "
        "A gene-to-trait association requires appropriate evidence "
        "and biological validation."
    )
