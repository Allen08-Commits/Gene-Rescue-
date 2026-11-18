
"""Gramene documented gene annotation search integration."""

from integrations import provenance, request_json

BASE_URL = "https://data.gramene.org"


def search_gramene_genes(
    query: str,
    limit: int = 10,
) -> dict:
    """Search Gramene gene annotations by keyword."""
    if not query.strip():
        raise ValueError("Enter a gene name or keyword.")

    if not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100.")

    endpoint = BASE_URL + "/genes"
    params = {
        "q": query.strip(),
        "fl": "_id,name,biotype,species,location",
        "size": limit,
    }

    data = request_json(endpoint, params=params)

    return {
        "query": query,
        "results": data,
        "provenance": provenance("Gramene", endpoint, params),
    }


def gramene_gene_url(gene_identifier: str) -> str:
    """Return a Gramene gene search URL for manual inspection."""
    if not gene_identifier.strip():
        raise ValueError("Enter a gene identifier.")

    from urllib.parse import quote

    return (
        "https://www.gramene.org/search?"
        f"q={quote(gene_identifier.strip())}"
    )
