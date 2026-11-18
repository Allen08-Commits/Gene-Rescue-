
"""InterPro integration for GeneRescue AI."""

from integrations import request_json, provenance

BASE_URL = "https://www.ebi.ac.uk/interpro/api"


def search_protein_accession(accession, page_size=50):
    """Retrieve InterPro matches for a UniProt protein accession."""

    if not accession or not accession.strip():
        raise ValueError("Protein accession is required.")

    if not 1 <= int(page_size) <= 200:
        raise ValueError("Page size must be between 1 and 200.")

    endpoint = (
        f"{BASE_URL}/protein/uniprot/"
        f"{accession.strip()}/"
    )

    params = {
        "page_size": int(page_size),
        "format": "json",
    }

    data = request_json(
        endpoint,
        params=params,
    )

    return {
        "database": "InterPro",
        "accession": accession,
        "matches": data.get("results", []),
        "count": len(data.get("results", [])),
        "next_page": data.get("next"),
        "provenance": provenance(
            "InterPro",
            endpoint,
            params,
        ),
    }


def get_protein_matches(accession, page_size=50):
    """Backward-compatible protein match retrieval."""
    return search_protein_accession(accession, page_size)


def get_interpro_entry(interpro_id):
    """Retrieve a specific InterPro entry."""

    if not interpro_id.startswith("IPR"):
        raise ValueError("Enter a valid InterPro accession.")

    endpoint = f"{BASE_URL}/entry/interpro/{interpro_id}/"

    params = {"format": "json"}

    data = request_json(endpoint, params=params)

    return {
        "database": "InterPro",
        "interpro_id": interpro_id,
        "record": data,
        "provenance": provenance(
            "InterPro",
            endpoint,
            params,
        ),
    }
