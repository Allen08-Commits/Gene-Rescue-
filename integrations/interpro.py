
"""InterPro API integration."""

from integrations import provenance, request_json

BASE_URL = "https://www.ebi.ac.uk/interpro/api"


def get_protein_matches(accession: str, page_size: int = 50) -> dict:
    """Retrieve InterPro matches associated with a UniProt protein."""
    if not accession.strip():
        raise ValueError("Enter a UniProt protein accession.")

    if not 1 <= page_size <= 200:
        raise ValueError("Page size must be between 1 and 200.")

    endpoint = (
        f"{BASE_URL}/protein/uniprot/{accession.strip()}/"
    )
    params = {
        "page_size": page_size,
        "format": "json",
    }

    data = request_json(endpoint, params=params)

    results = data.get("results", [])

    return {
        "accession": accession,
        "matches": results,
        "record_count": len(results),
        "next_page": data.get("next"),
        "previous_page": data.get("previous"),
        "provenance": provenance("InterPro", endpoint, params),
    }


def get_interpro_entry(interpro_id: str) -> dict:
    """Retrieve information about a specific InterPro entry."""
    if not interpro_id.startswith("IPR"):
        raise ValueError("Enter a valid InterPro accession, e.g. IPRxxxxx.")

    endpoint = f"{BASE_URL}/entry/interpro/{interpro_id}/"
    params = {"format": "json"}

    data = request_json(endpoint, params=params)

    return {
        "interpro_id": interpro_id,
        "record": data,
        "provenance": provenance("InterPro", endpoint, params),
    }
