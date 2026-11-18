
"""Gramene resource links for GeneRescue AI."""

from urllib.parse import quote


def resource_links(query):
    """Return clearly labelled external resource search links."""

    if not query or not query.strip():
        raise ValueError("Enter a crop, gene or trait.")

    encoded = quote(query.strip())

    return [
        {
            "name": "Gramene",
            "url": (
                "https://www.gramene.org/search?"
                f"q={encoded}"
            ),
            "note": (
                "Search Gramene's crop genomics and "
                "comparative genomics resources."
            ),
        },
        {
            "name": "Ensembl Plants",
            "url": (
                "https://plants.ensembl.org/Multi/Search/Results?"
                f"q={encoded}"
            ),
            "note": (
                "Search plant genome and gene resources."
            ),
        },
        {
            "name": "NCBI",
            "url": (
                "https://www.ncbi.nlm.nih.gov/search/all/?term="
                f"{encoded}"
            ),
            "note": (
                "Search NCBI biological records and resources."
            ),
        },
    ]
