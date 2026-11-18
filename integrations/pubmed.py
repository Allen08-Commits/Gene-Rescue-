
"""PubMed integration for GeneRescue AI."""

import os
import xml.etree.ElementTree as ET
import streamlit as st

from integrations import (
    request_json,
    request_text,
    provenance,
    ExternalDatabaseError,
)

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def _params(values):
    params = dict(values)
    params["tool"] = "GeneRescueAI"

    try:
        email = str(
            st.secrets.get("NCBI_EMAIL", os.getenv("NCBI_EMAIL", ""))
        ).strip()
        api_key = str(
            st.secrets.get("NCBI_API_KEY", os.getenv("NCBI_API_KEY", ""))
        ).strip()
    except Exception:
        email = os.getenv("NCBI_EMAIL", "").strip()
        api_key = os.getenv("NCBI_API_KEY", "").strip()

    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key

    return params


def search_literature(query, limit=10):
    """Search PubMed and return article metadata."""
    if not query or not query.strip():
        raise ValueError("Enter a literature search query.")

    if not 1 <= int(limit) <= 100:
        raise ValueError("Limit must be between 1 and 100.")

    endpoint = BASE_URL + "esearch.fcgi"
    params = _params({
        "db": "pubmed",
        "term": query.strip(),
        "retmax": int(limit),
        "retmode": "json",
        "sort": "relevance",
    })

    data = request_json(endpoint, params=params)
    result = data.get("esearchresult", {})
    ids = result.get("idlist", [])

    if not ids:
        return []

    articles = fetch_articles(ids)

    return articles


def fetch_articles(pmids):
    """Retrieve article titles, journals, dates and abstracts."""
    if not pmids:
        return []

    endpoint = BASE_URL + "efetch.fcgi"
    params = _params({
        "db": "pubmed",
        "id": ",".join(str(pmid) for pmid in pmids),
        "retmode": "xml",
    })

    content = request_text(endpoint, params=params)

    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise ExternalDatabaseError(
            "PubMed returned invalid XML."
        ) from exc

    articles = []

    for article in root.findall(".//PubmedArticle"):

        def value(path):
            element = article.find(path)
            if element is None:
                return ""
            return " ".join(
                text.strip()
                for text in element.itertext()
                if text.strip()
            )

        pmid = value(".//PMID")
        title = value(".//ArticleTitle")
        journal = value(".//Journal/Title")

        year = (
            value(".//PubDate/Year")
            or value(".//PubDate/MedlineDate")
        )

        abstract_parts = []

        for element in article.findall(".//Abstract/AbstractText"):
            text = " ".join(
                part.strip()
                for part in element.itertext()
                if part.strip()
            )

            if text:
                label = element.attrib.get("Label", "")
                abstract_parts.append(
                    f"{label}: {text}" if label else text
                )

        articles.append({
            "pmid": pmid,
            "title": title,
            "journal": journal,
            "year": year,
            "abstract": " ".join(abstract_parts),
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        })

    return articles


def search_pubmed(query, limit=10):
    """Backward-compatible PubMed search."""
    return search_literature(query, limit)
