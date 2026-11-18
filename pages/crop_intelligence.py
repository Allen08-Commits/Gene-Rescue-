
"""GeneRescue AI - Crop Intelligence."""

import pandas as pd
import streamlit as st

from integrations import pubmed, gramene

from services.session_manager import create_research_session


def render():
    st.title("Crop Intelligence")

    st.write(
        "Investigate crop-associated traits through scientific "
        "literature and publicly available crop genomics resources."
    )

    st.warning(
        "Literature co-mention does not establish a causal "
        "gene-to-trait relationship. Candidate hypotheses require "
        "independent biological evidence."
    )

    species = st.text_input(
        "Crop species",
        placeholder="e.g. Oryza sativa",
    )

    trait = st.text_input(
        "Research trait",
        placeholder="e.g. drought tolerance",
    )

    limit = st.number_input(
        "Maximum PubMed articles",
        min_value=1,
        max_value=100,
        value=15,
    )

    if st.button(
        "Retrieve Crop Evidence",
        type="primary",
        disabled=not species.strip() or not trait.strip(),
    ):
        query = (
            f'("{species}"[Title/Abstract]) '
            f'AND ("{trait}"[Title/Abstract])'
        )

        try:
            with st.spinner("Searching scientific literature..."):
                papers = pubmed.search_literature(
                    query,
                    limit=int(limit),
                )

            st.divider()
            st.subheader("PubMed literature results")

            if papers:
                st.metric(
                    "Articles retrieved",
                    len(papers),
                )

                st.dataframe(
                    pd.DataFrame(papers),
                    use_container_width=True,
                    hide_index=True,
                )

                for paper in papers:
                    if paper.get("url"):
                        st.markdown(
                            f"[Open article: {paper.get('title', paper.get('pmid'))}]"
                            f"({paper['url']})"
                        )
            else:
                st.info(
                    "No PubMed records were returned for this query."
                )

            st.divider()
            st.subheader("Gramene crop genomics resource")

            resource_results = gramene.resource_links(
                f"{species} {trait}"
            )

            for item in resource_results:
                st.markdown(
                    f"[{item['name']}]({item['url']})"
                )
                st.caption(item["note"])

            st.session_state["last_crop_evidence"] = {
                "species": species,
                "trait": trait,
                "literature": papers,
                "gramene": resource_results,
            }

            create_research_session(
                tool_name="Crop Intelligence",
                session_title=f"{species}: {trait}",
                input_summary=(
                    f"Species: {species}; Trait: {trait}"
                ),
                result_summary=(
                    f"{len(papers)} PubMed records retrieved."
                ),
            )

            st.success("Crop evidence search completed.")

        except Exception as error:
            st.error(
                f"Crop evidence retrieval failed: {error}"
            )

    st.caption(
        "Check each publication's organism, cultivar, tissue, "
        "experimental conditions and evidence before drawing conclusions."
    )
