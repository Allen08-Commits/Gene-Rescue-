
"""NCBI Entrez E-utilities integration."""

import os
import xml.etree.ElementTree as ET

import streamlit as st

from integrations import (
    ExternalDatabaseError,
    provenance,
    request_json,
    request_text,
)

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def _setting(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, os.getenv(name, default)))
    except Exception:
        return os.getenv(name, default)


def _params(extra: dict) -> dict:
    params = dict(extra)

    email = _setting("NCBI_EMAIL")
    api_key = _setting("NCBI_API_KEY")

    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key

    params["tool"] = "GeneRescueAI"
    return params


def search_ncbi(
    query: str,
    database: str = "gene",
    limit: int = 10,
) -> dict:
    """Search an NCBI Entrez database and return matching identifiers."""
    if not query or not query.strip():
        raise ValueError("Enter a search term.")

    allowed = {
        "gene", "nuccore", "protein", "assembly",
        "sra", "biosample", "bioproject", "pubmed",
    }
    if database not in allowed:
        raise ValueError(f"Unsupported NCBI database: {database}")

    if not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100.")

    endpoint = BASE_URL + "esearch.fcgi"
    params = _params({
        "db": database,
        "term": query.strip(),
        "retmax": limit,
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


def fetch_ncbi_summary(
    ids: list[str],
    database: str = "gene",
) -> dict:
    """Retrieve summaries for a list of Entrez identifiers."""
    if not ids:
        raise ValueError("At least one NCBI identifier is required.")

    endpoint = BASE_URL + "esummary.fcgi"
    params = _params({
        "db": database,
        "id": ",".join(str(item) for item in ids),
        "retmode": "json",
    })

    data = request_json(endpoint, params=params)
    result = data.get("result", {})
    summaries = [
        result[item]
        for item in result.get("uids", [])
        if item in result
    ]

    return {
        "database": database,
        "records": summaries,
        "record_count": len(summaries),
        "provenance": provenance("NCBI Entrez", endpoint, params),
    }


def fetch_ncbi_record(
    identifier: str,
    database: str = "nuccore",
    rettype: str = "gb",
    retmode: str = "text",
) -> dict:
    """Retrieve a full NCBI record, such as a GenBank or FASTA record."""
    if not identifier or not identifier.strip():
        raise ValueError("Enter an accession or NCBI identifier.")

    if database not in {"nuccore", "protein"}:
        raise ValueError("Record retrieval supports nuccore or protein.")

    endpoint = BASE_URL + "efetch.fcgi"
    params = _params({
        "db": database,
        "id": identifier.strip(),
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


def fetch_ncbi_gene_xml(gene_id: str) -> dict:
    """Retrieve an NCBI Gene record in XML format."""
    endpoint = BASE_URL + "efetch.fcgi"
    params = _params({
        "db": "gene",
        "id": gene_id,
        "retmode": "xml",
    })

    content = request_text(endpoint, params=params)

    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise ExternalDatabaseError(
            "NCBI returned invalid Gene XML."
        ) from exc

    return {
        "gene_id": gene_id,
        "xml": ET.tostring(root, encoding="unicode"),
        "provenance": provenance("NCBI Gene", endpoint, params),
    }
