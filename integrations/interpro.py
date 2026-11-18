
"""InterPro API integration."""

from urllib.parse import quote

from integrations import request_json, provenance


BASE_URL = "https://www.ebi.ac.uk/interpro/api"


def search_protein_accession(accession, page_size=50):
    """Retrieve InterPro matches for a UniProt accession."""
    if not str(accession).strip():
        raise ValueError("A protein accession is required.")

    endpoint = (
        f"{BASE_URL}/protein/uniprot/"
        f"{quote(str(accession), safe='')}/"
    )

    page_size = max(1, min(int(page_size), 200))

    data = request_json(
        endpoint,
        params={
            "page_size": page_size,
        },
    )

    matches = []

    for item in data.get("results", []):
        metadata = item.get("metadata", {})
        proteins = item.get("proteins", [])

        matches.append({
            "accession": metadata.get("accession", ""),
            "name": metadata.get("name", ""),
            "type": metadata.get("type", ""),
            "source_database": metadata.get("source_database", ""),
            "protein_accession": accession,
            "proteins": proteins,
            "source_url": item.get("metadata", {}).get("url", ""),
            "raw_record": item,
        })

    return {
        "protein_accession": accession,
        "matches": matches,
        "count": len(matches),
        "next": data.get("next"),
        "provenance": provenance(
            "InterPro",
            endpoint,
            accession,
        ),
    }


def get_protein_matches(accession, page_size=50):
    """Compatibility wrapper for protein match retrieval."""
    return search_protein_accession(
        accession,
        page_size=page_size,
    )


def get_interpro_entry(interpro_accession):
    """Retrieve metadata for an InterPro entry."""
    endpoint = (
        f"{BASE_URL}/entry/interpro/"
        f"{quote(str(interpro_accession), safe='')}/"
    )

    data = request_json(endpoint)

    return {
        "accession": interpro_accession,
        "record": data,
        "provenance": provenance(
            "InterPro",
            endpoint,
            interpro_accession,
        ),
    }
