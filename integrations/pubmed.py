
"""PubMed literature search integration."""

import xml.etree.ElementTree as ET

from integrations import (
    request_json,
    request_text,
    ncbi_parameters,
    provenance,
)


BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def search_literature(query, limit=10):
    """Search PubMed and return matching PMID identifiers."""
    if not str(query).strip():
        raise ValueError("Enter a literature search query.")

    params = {
        **ncbi_parameters(),
        "db": "pubmed",
        "term": str(query),
        "retmode": "json",
        "retmax": max(1, min(int(limit), 100)),
        "sort": "relevance",
    }

    data = request_json(
        f"{BASE_URL}/esearch.fcgi",
        params=params,
    )

    result = data.get("esearchresult", {})
    pmids = result.get("idlist", [])

    if not pmids:
        return []

    return fetch_articles(pmids)


def fetch_articles(pmids):
    """Fetch PubMed article metadata for PMID identifiers."""
    identifiers = [
        str(pmid).strip()
        for pmid in pmids
        if str(pmid).strip()
    ]

    if not identifiers:
        return []

    params = {
        **ncbi_parameters(),
        "db": "pubmed",
        "id": ",".join(identifiers),
        "retmode": "xml",
    }

    xml_text = request_text(
        f"{BASE_URL}/efetch.fcgi",
        params=params,
    )

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ValueError(
            "PubMed returned an unreadable XML response."
        ) from exc

    articles = []

    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID", default="")

        title_element = article.find(".//ArticleTitle")
        title = (
            "".join(title_element.itertext())
            if title_element is not None else ""
        )

        journal = article.findtext(
            ".//Journal/Title",
            default="",
        )

        year = (
            article.findtext(
                ".//JournalIssue/PubDate/Year",
                default="",
            )
            or article.findtext(
                ".//JournalIssue/PubDate/MedlineDate",
                default="",
            )
        )

        abstract_parts = []

        for abstract_element in article.findall(
            ".//Abstract/AbstractText"
        ):
            label = abstract_element.attrib.get("Label", "")
            content = "".join(abstract_element.itertext())

            if label:
                abstract_parts.append(f"{label}: {content}")
            else:
                abstract_parts.append(content)

        abstract = " ".join(abstract_parts)

        articles.append({
            "pmid": pmid,
            "title": title,
            "journal": journal,
            "year": year,
            "abstract": abstract,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "source": "PubMed",
        })

    return articles


def search_pubmed(query, limit=10):
    """Compatibility wrapper for literature search."""
    return {
        "query": query,
        "articles": search_literature(query, limit=limit),
        "provenance": provenance(
            "PubMed",
            "esearch.fcgi and efetch.fcgi",
            query,
        ),
    }
