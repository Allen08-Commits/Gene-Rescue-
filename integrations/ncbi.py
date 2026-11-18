
"""NCBI integration for GeneRescue AI."""

import os
import streamlit as st

from integrations import (
    request_json,
    request_text,
    provenance,
    ExternalDatabaseError,
)

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def _setting(name):
    try:
        return str(st.secrets.get(name, os.getenv(name, ""))).strip()
    except Exception:
        return os.getenv(name, "").strip()


def _params(values):
    params = dict(values)
    params["tool"] = "GeneRescueAI"

    email = _setting("NCBI_EMAIL")
    api_key = _setting("NCBI_API_KEY")

    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key

    return params


def _search(query, database, retmax=10):
    if not query or not query.strip():
        raise ValueError("Enter a search query.")

    if not 1 <= int(retmax) <= 100:
        raise ValueError("Maximum records must be between 1 and 100.")

    endpoint = BASE_URL + "esearch.fcgi"
    params = _params({
        "db": database,
        "term": query.strip(),
        "retmax": int(retmax),
        "retmode": "json",
    })

    data = request_json(endpoint, params=params)
    result = data.get("esearchresult", {})

    return {
        "database": database,
        "query": query,
        "count": int(result.get("count", 0)),
        "ids": result.get("idlist", []),
        "provenance": provenance("NCBI Entrez", endpoint, params),
    }


def search_gene(query, organism=None, retmax=10):
    """Search NCBI Gene records."""
    search_term = query.strip()

    if organism:
        search_term += f" AND {organism.strip()}[Organism]"

    return _search(search_term, "gene", retmax)


def search_nucleotide(query, retmax=10):
    """Search NCBI nucleotide records."""
    return _search(query, "nuccore", retmax)


def search_protein(query, retmax=10):
    """Search NCBI protein records."""
    return _search(query, "protein", retmax)


def fetch_summaries(ids, database="gene"):
    """Retrieve summaries for Entrez identifiers."""
    if not ids:
        return []

    endpoint = BASE_URL + "esummary.fcgi"
    params = _params({
        "db": database,
        "id": ",".join(str(item) for item in ids),
        "retmode": "json",
    })

    data = request_json(endpoint, params=params)
    result = data.get("result", {})

    records = [
        result[item]
        for item in result.get("uids", [])
        if item in result
    ]

    return {
        "records": records,
        "count": len(records),
        "provenance": provenance("NCBI Entrez", endpoint, params),
    }


def fetch_record(identifier, database="nuccore",
                 rettype="gb", retmode="text"):
    """Retrieve a GenBank, FASTA or other supported record."""
    if database not in {"nuccore", "protein", "gene"}:
        raise ValueError("Unsupported NCBI database.")

    endpoint = BASE_URL + "efetch.fcgi"
    params = _params({
        "db": database,
        "id": str(identifier).strip(),
        "rettype": rettype,
        "retmode": retmode,
    })

    content = request_text(endpoint, params=params)

    return {
        "identifier": identifier,
        "database": database,
        "content": content,
        "provenance": provenance("NCBI Entrez", endpoint, params),
    }


# Backward-compatible function names

def search_ncbi(query, database="gene", limit=10):
    return _search(query, database, limit)


def fetch_ncbi_summary(ids, database="gene"):
    return fetch_summaries(ids, database)


def fetch_ncbi_record(identifier, database="nuccore",
                      rettype="gb", retmode="text"):
    return fetch_record(identifier, database, rettype, retmode)
