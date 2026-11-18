
"""NCBI Entrez database integration."""

from urllib.parse import urlencode

from integrations import (
    request_json,
    request_text,
    ncbi_parameters,
    provenance,
    ExternalDatabaseError,
)

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _search(query, database="gene", retmax=10):
    if not str(query).strip():
        raise ValueError("Enter a search query.")

    params = {
        **ncbi_parameters(),
        "db": database,
        "term": str(query),
        "retmode": "json",
        "retmax": max(1, min(int(retmax), 100)),
    }

    data = request_json(
        f"{BASE_URL}/esearch.fcgi",
        params=params,
    )

    result = data.get("esearchresult", {})
    ids = result.get("idlist", [])

    return {
        "database": database,
        "query": query,
        "count": int(result.get("count", 0)),
        "ids": ids,
        "provenance": provenance(
            "NCBI Entrez",
            "esearch.fcgi",
            query,
        ),
    }


def search_gene(query, organism=None, retmax=10):
    """Search NCBI Gene records."""
    term = str(query).strip()

    if organism:
        term = f"({term}) AND {organism}[Organism]"

    return _search(term, database="gene", retmax=retmax)


def search_nucleotide(query, retmax=10):
    return _search(query, database="nuccore", retmax=retmax)


def search_protein(query, retmax=10):
    return _search(query, database="protein", retmax=retmax)


def fetch_summaries(ids, database="gene"):
    """Retrieve NCBI summaries for a collection of record IDs."""
    ids = [str(item) for item in ids if str(item).strip()]

    if not ids:
        return []

    params = {
        **ncbi_parameters(),
        "db": database,
        "id": ",".join(ids),
        "retmode": "json",
    }

    data = request_json(
        f"{BASE_URL}/esummary.fcgi",
        params=params,
    )

    result = data.get("result", {})
    summaries = []

    for identifier in result.get("uids", []):
        record = result.get(identifier, {})
        summaries.append({
            "id": identifier,
            "record": record,
            "source": "NCBI Entrez",
        })

    return summaries


def fetch_record(
    identifier,
    database="nuccore",
    rettype="gb",
    retmode="text",
):
    """Fetch a full NCBI record in the requested format."""
    if not str(identifier).strip():
        raise ValueError("A record identifier is required.")

    params = {
        **ncbi_parameters(),
        "db": database,
        "id": str(identifier),
        "rettype": rettype,
        "retmode": retmode,
    }

    text = request_text(
        f"{BASE_URL}/efetch.fcgi",
        params=params,
    )

    return {
        "identifier": str(identifier),
        "database": database,
        "content": text,
        "provenance": provenance(
            "NCBI Entrez",
            "efetch.fcgi",
            identifier,
        ),
    }


def search_ncbi(query, database="gene", limit=10):
    """Compatibility wrapper for general NCBI searches."""
    return _search(query, database=database, retmax=limit)


def fetch_ncbi_summary(ids, database="gene"):
    return fetch_summaries(ids, database=database)


def fetch_ncbi_record(
    identifier,
    database="nuccore",
    rettype="gb",
    retmode="text",
):
    return fetch_record(
        identifier,
        database=database,
        rettype=rettype,
        retmode=retmode,
    )
