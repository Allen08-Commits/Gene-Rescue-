
"""UniProt REST API integration for GeneRescue AI.

Features:
- Search UniProtKB protein records
- Filter by organism taxonomy ID
- Filter for reviewed (Swiss-Prot) records
- Retrieve a protein entry by accession
- Retrieve a protein sequence in FASTA format
- Retrieve additional search pages
- Preserve query and retrieval provenance

Official API:
https://rest.uniprot.org
"""

from urllib.parse import quote

from integrations import (
    ExternalDatabaseError,
    provenance,
    request_json,
    request_text,
)

BASE_URL = "https://rest.uniprot.org"
SEARCH_ENDPOINT = f"{BASE_URL}/uniprotkb/search"


def _validate_text(value: str, field_name: str) -> str:
    """Validate and normalize a required text parameter."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required.")
    return value.strip()


def _validate_limit(limit: int) -> int:
    """Validate the maximum number of records per request."""
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ValueError("Limit must be an integer.")

    if not 1 <= limit <= 500:
        raise ValueError("Limit must be between 1 and 500.")

    return limit


def _build_search_query(
    query: str,
    organism_id: int | None = None,
    reviewed_only: bool = False,
) -> str:
    """Build a UniProt query using supported search syntax."""
    search_query = _validate_text(query, "Search query")

    if organism_id is not None:
        if isinstance(organism_id, bool) or not isinstance(
            organism_id, int
        ):
            raise ValueError("Organism ID must be an integer.")

        if organism_id <= 0:
            raise ValueError("Organism ID must be positive.")

        search_query += f" AND organism_id:{organism_id}"

    if reviewed_only:
        search_query += " AND reviewed:true"

    return search_query


def search_proteins(
    query: str,
    organism_id: int | None = None,
    reviewed_only: bool = False,
    limit: int = 10,
    fields: list[str] | None = None,
) -> dict:
    """Search UniProtKB and return protein records.

    Args:
        query:
            UniProt search expression, protein name, gene name,
            accession or other supported search term.

        organism_id:
            Optional NCBI taxonomy identifier.

        reviewed_only:
            If True, restrict results to reviewed UniProtKB records.

        limit:
            Maximum number of results to retrieve (1-500).

        fields:
            Optional list of UniProt field names to return.
            When omitted, UniProt's default fields are returned.

    Returns:
        Dictionary containing query, records, count and provenance.
    """
    limit = _validate_limit(limit)

    if not isinstance(reviewed_only, bool):
        raise ValueError("reviewed_only must be True or False.")

    search_query = _build_search_query(
        query=query,
        organism_id=organism_id,
        reviewed_only=reviewed_only,
    )

    params = {
        "query": search_query,
        "format": "json",
        "size": limit,
    }

    if fields is not None:
        if not isinstance(fields, list) or not fields:
            raise ValueError("Fields must be a non-empty list.")

        cleaned_fields = [
            _validate_text(field, "Field name")
            for field in fields
        ]
        params["fields"] = ",".join(cleaned_fields)

    data = request_json(
        SEARCH_ENDPOINT,
        params=params,
    )

    records = data.get("results", [])

    return {
        "database": "UniProtKB",
        "query": search_query,
        "records": records,
        "record_count": len(records),
        "result_count": data.get("facets", []),
        "next_page": data.get("next"),
        "previous_page": data.get("previous"),
        "provenance": provenance(
            source="UniProtKB",
            endpoint=SEARCH_ENDPOINT,
            query=params,
        ),
    }


def get_protein_entry(accession: str) -> dict:
    """Retrieve a complete UniProtKB entry by accession.

    Args:
        accession: UniProt accession such as a protein entry ID.

    Returns:
        Protein record with source provenance.
    """
    accession = _validate_text(accession, "UniProt accession")

    safe_accession = quote(accession, safe="")
    endpoint = f"{BASE_URL}/uniprotkb/{safe_accession}"

    params = {"format": "json"}

    data = request_json(
        endpoint,
        params=params,
    )

    return {
        "database": "UniProtKB",
        "accession": accession,
        "record": data,
        "provenance": provenance(
            source="UniProtKB",
            endpoint=endpoint,
            query=params,
        ),
    }


def get_protein_fasta(accession: str) -> dict:
    """Retrieve the amino-acid sequence in FASTA format.

    Args:
        accession: UniProt accession.

    Returns:
        FASTA text, accession and provenance.
    """
    accession = _validate_text(accession, "UniProt accession")

    safe_accession = quote(accession, safe="")
    endpoint = f"{BASE_URL}/uniprotkb/{safe_accession}.fasta"

    fasta_content = request_text(endpoint)

    if not fasta_content.strip().startswith(">"):
        raise ExternalDatabaseError(
            "UniProt did not return a valid FASTA response."
        )

    return {
        "database": "UniProtKB",
        "accession": accession,
        "fasta": fasta_content.strip(),
        "provenance": provenance(
            source="UniProtKB",
            endpoint=endpoint,
            query={},
        ),
    }


def get_next_search_page(next_url: str) -> dict:
    """Retrieve the next page from a UniProt search response.

    The URL must come directly from the next_page value returned
    by search_proteins or a previous page retrieval.
    """
    next_url = _validate_text(next_url, "Next-page URL")

    if not next_url.startswith(
        "https://rest.uniprot.org/uniprotkb/search"
    ):
        raise ValueError(
            "The next-page URL must be a UniProtKB search URL."
        )

    data = request_json(next_url)

    records = data.get("results", [])

    return {
        "database": "UniProtKB",
        "records": records,
        "record_count": len(records),
        "next_page": data.get("next"),
        "previous_page": data.get("previous"),
        "provenance": provenance(
            source="UniProtKB",
            endpoint=next_url,
            query="Pagination request",
        ),
    }
