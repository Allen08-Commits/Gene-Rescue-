
"""PubMed literature search using NCBI E-utilities."""

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
    params["tool"] = "GeneRescueAI"

    email = _setting("NCBI_EMAIL")
    api_key = _setting("NCBI_API_KEY")

    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key

    return params


def search_pubmed(
    query: str,
    limit: int = 10,
) -> dict:
    """Search PubMed and return matching PMIDs."""
    if not query.strip():
        raise ValueError("Enter a literature search query.")

    if not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100.")

    endpoint = BASE_URL + "esearch.fcgi"
    params = _params({
        "db": "pubmed",
        "term": query.strip(),
        "retmax": limit,
        "retmode": "json",
        "sort": "relevance",
    })

    data = request_json(endpoint, params=params)
    result = data.get("esearchresult", {})

    return {
        "query": query,
        "count": int(result.get("count", 0)),
        "pmids": result.get("idlist", []),
        "provenance": provenance("PubMed", endpoint, params),
    }


def fetch_pubmed_articles(pmids: list[str]) -> dict:
    """Retrieve article titles, journal details and available abstracts."""
    if not pmids:
        raise ValueError("At least one PMID is required.")

    endpoint = BASE_URL + "efetch.fcgi"
    params = _params({
        "db": "pubmed",
        "id": ",".join(str(pmid) for pmid in pmids),
        "retmode": "xml",
    })

    xml_content = request_text(endpoint, params=params)

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as exc:
        raise ExternalDatabaseError(
            "PubMed returned invalid XML."
        ) from exc

    articles = []

    for article in root.findall(".//PubmedArticle"):
        def get_text(path: str) -> str:
            element = article.find(path)
            if element is None:
                return ""
            return " ".join(
                part.strip()
                for part in element.itertext()
                if part.strip()
            )

        pmid = get_text(".//PMID")
        title = get_text(".//ArticleTitle")
        journal = get_text(".//Journal/Title")
        year = (
            get_text(".//PubDate/Year")
            or get_text(".//PubDate/MedlineDate")
        )

        abstract_parts = []
        for part in article.findall(".//Abstract/AbstractText"):
            text = " ".join(
                value.strip()
                for value in part.itertext()
                if value.strip()
            )
            label = part.attrib.get("Label", "")
            if text:
                abstract_parts.append(
                    f"{label}: {text}" if label else text
                )

        articles.append({
            "pmid": pmid,
            "title": title,
            "journal": journal,
            "year": year,
            "abstract": "\n".join(abstract_parts),
            "pubmed_url": (
                f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                if pmid else ""
            ),
        })

    return {
        "articles": articles,
        "record_count": len(articles),
        "provenance": provenance("PubMed", endpoint, params),
    }
