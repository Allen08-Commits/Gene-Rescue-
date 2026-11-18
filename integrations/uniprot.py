
"""UniProt REST API integration."""

from integrations import provenance, request_json, request_text

BASE_URL = "https://rest.uniprot.org"


def search_proteins(
    query: str,
    organism_id: int | None = None,
    reviewed_only: bool = False,
    limit: int = 10,
) -> dict:
    """Search UniProtKB for protein records."""
    if not query.strip():
        raise ValueError("Enter a protein or gene search term.")

    if not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100.")

    search_query = query.strip()

    if organism_id is not None:
        search_query += f" AND organism_id:{int(organism_id)}"

    if reviewed_only:
        search_query += " AND reviewed:true"

    endpoint = BASE_URL + "/uniprotkb/search"
    params = {
        "query": search_query,
        "format": "json",
        "size": limit,
    }

    data = request_json(endpoint, params=params)

    return {
        "query": search_query,
        "records": data.get("results", []),
        "record_count": len(data.get("results", [])),
        "total_count": data.get("results", [{}])[0].get(
            "entryType"
        ) if data.get("results") else None,
        "provenance": provenance("UniProtKB", endpoint, params),
    }


def get_protein_entry(accession: str) -> dict:
    """Retrieve a UniProtKB entry by accession."""
    if not accession.strip():
        raise ValueError("Enter a UniProt accession.")

    endpoint = f"{BASE_URL}/uniprotkb/{accession.strip()}"
    params = {"format": "json"}

    data = request_json(endpoint, params=params)

    return {
        "accession": accession,
        "record": data,
        "provenance": provenance("UniProtKB", endpoint, params),
    }


def get_protein_fasta(accession: str) -> dict:
    """Retrieve the amino-acid sequence in FASTA format."""
    if not accession.strip():
        raise ValueError("Enter a UniProt accession.")

    endpoint = f"{BASE_URL}/uniprotkb/{accession.strip()}.fasta"
    fasta = request_text(endpoint)

    return {
        "accession": accession,
        "fasta": fasta,
        "provenance": provenance("UniProtKB", endpoint, {}),
    }
