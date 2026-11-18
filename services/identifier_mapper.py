
"""Cross-database gene and protein identifier lookup."""

from integrations import ensembl_plants, uniprot


def map_identifier(identifier, species="oryza_sativa"):
    """Search a supplied identifier across supported resources."""

    identifier = str(identifier).strip()

    if not identifier:
        raise ValueError("Enter a gene or protein identifier.")

    results = {
        "input_identifier": identifier,
        "species": species,
        "ensembl_results": [],
        "uniprot_results": [],
        "warnings": [],
    }

    try:
        results["ensembl_results"] = (
            ensembl_plants.search_plant_genes(
                identifier,
                species=species,
            )
        )
    except Exception as exc:
        results["warnings"].append(
            f"Ensembl Plants lookup failed: {exc}"
        )

    try:
        results["uniprot_results"] = (
            uniprot.search_proteins(
                identifier,
                size=10,
            )
        )
    except Exception as exc:
        results["warnings"].append(
            f"UniProt lookup failed: {exc}"
        )

    results["interpretation"] = (
        "These are candidate database matches. Verify organism, "
        "accession and sequence before treating records as "
        "the same biological entity."
    )

    return results
