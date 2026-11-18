 
"""Session-only evidence management for GeneRescue AI."""

from datetime import datetime, timezone
from urllib.parse import quote
import uuid

VALID_EVIDENCE_CLASSES = {
    "experimental",
    "curated_annotation",
    "computational_prediction",
    "database_annotation",
    "literature",
}


def classify_evidence(
    source_database: str,
    evidence_type: str,
) -> str:
    """Assign a conservative evidence category."""

    source = source_database.strip().lower()
    evidence = evidence_type.strip().lower()

    if source == "pubmed" or "article" in evidence:
        return "literature"

    if "experimental" in evidence or "assay" in evidence:
        return "experimental"

    if source in {"uniprot", "interpro", "gramene"}:
        return "curated_annotation"

    if "prediction" in evidence or "predicted" in evidence:
        return "computational_prediction"

    return "database_annotation"


def save_evidence(
    source_database: str,
    source_identifier: str,
    evidence_type: str,
    evidence_title: str = "",
    evidence_description: str = "",
    source_url: str = "",
    retrieval_query: dict | None = None,
    evidence_payload: dict | list | None = None,
    evidence_class: str | None = None,
    project_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    """Save an evidence record in the current app session."""

    if not source_database.strip():
        raise ValueError("Source database is required.")

    if not evidence_type.strip():
        raise ValueError("Evidence type is required.")

    category = evidence_class or classify_evidence(
        source_database,
        evidence_type,
    )

    if category not in VALID_EVIDENCE_CLASSES:
        raise ValueError("Invalid evidence classification.")

    record = {
        "id": str(uuid.uuid4()),
        "source_database": source_database.strip(),
        "source_identifier": source_identifier or "",
        "evidence_type": evidence_type.strip(),
        "evidence_title": evidence_title or "",
        "evidence_description": evidence_description or "",
        "source_url": source_url or "",
        "retrieval_query": retrieval_query or {},
        "evidence_payload": evidence_payload or {},
        "evidence_class": category,
        "project_id": project_id,
        "session_id": session_id,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }

    import streamlit as st

    if "research_evidence" not in st.session_state:
        st.session_state["research_evidence"] = []

    st.session_state["research_evidence"].insert(0, record)

    return record


def list_evidence(
    project_id: str | None = None,
    session_id: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """Return evidence records from the current app session."""

    if not 1 <= limit <= 500:
        raise ValueError("Limit must be between 1 and 500.")

    import streamlit as st

    records = st.session_state.get("research_evidence", [])

    if project_id:
        records = [
            item for item in records
            if item.get("project_id") == project_id
        ]

    if session_id:
        records = [
            item for item in records
            if item.get("session_id") == session_id
        ]

    return records[:limit]


def evidence_source_link(database: str, identifier: str) -> str:
    """Build source links for supported database identifiers."""

    database = database.strip().lower()
    identifier = quote((identifier or "").strip(), safe="")

    if not identifier:
        return ""

    links = {
        "ncbi_gene": f"https://www.ncbi.nlm.nih.gov/gene/{identifier}",
        "ncbi_nucleotide": f"https://www.ncbi.nlm.nih.gov/nuccore/{identifier}",
        "ncbi_protein": f"https://www.ncbi.nlm.nih.gov/protein/{identifier}",
        "uniprot": f"https://www.uniprot.org/uniprotkb/{identifier}",
        "interpro": f"https://www.ebi.ac.uk/interpro/entry/InterPro/{identifier}",
        "pubmed": f"https://pubmed.ncbi.nlm.nih.gov/{identifier}/",
        "ensembl": f"https://plants.ensembl.org/id/{identifier}",
    }

    return links.get(database, "")
