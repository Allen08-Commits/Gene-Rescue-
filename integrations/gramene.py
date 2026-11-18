
"""Gramene and plant genomics resource links."""

from urllib.parse import quote


def resource_links(query):
    """Generate direct search links for plant genomics resources."""
    term = quote(str(query).strip())

    if not term:
        raise ValueError("Enter a gene, organism or crop name.")

    return [
        {
            "name": "Gramene",
            "url": f"https://www.gramene.org/search?query={term}",
            "note": (
                "Plant comparative genomics and crop information. "
                "The link opens the Gramene resource."
            ),
        },
        {
            "name": "Ensembl Plants",
            "url": (
                "https://plants.ensembl.org/Multi/Search/Results?"
                f"q={term}"
            ),
            "note": (
                "Search plant genomes, genes and genomic features."
            ),
        },
        {
            "name": "NCBI",
            "url": (
                "https://www.ncbi.nlm.nih.gov/search/all/?term="
                f"{term}"
            ),
            "note": (
                "Search NCBI biological records and publications."
            ),
        },
        {
            "name": "UniProt",
            "url": (
                "https://www.uniprot.org/uniprotkb?"
                f"query={term}"
            ),
            "note": (
                "Search protein sequences and functional annotations."
            ),
        },
    ]


def gramene_gene_url(identifier):
    """Return a Gramene search URL for a gene or accession."""
    term = quote(str(identifier).strip())

    if not term:
        raise ValueError("A gene identifier is required.")

    return f"https://www.gramene.org/search?query={term}"
