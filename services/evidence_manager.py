
"""Research evidence management and provenance."""

from datetime import datetime, timezone
from urllib.parse import quote
from uuid import uuid4

import streamlit as st


def _records():
    if "research_evidence" not in st.session_state:
        st.session_state["research_evidence"] = []

    return st.session_state["research_evidence"]


def classify_evidence(database, record_type=""):
    """Classify evidence by its source and record type."""

    text = f"{database} {record_type}".lower()

    if any(term in text for term in [
        "ncbi", "gene", "genome", "ensembl"
    ]):
        return "Gene/genomic evidence"

    if any(term in text for term in [
        "uniprot", "protein", "interpro"
    ]):
        return "Protein/function evidence"

    if any(term in text for term in [
        "pubmed", "publication", "article"
    ]):
        return "Literature evidence"

    if any(term in text for term in [
        "gramene", "plant", "crop", "trait"
    ]):
        return "Plant/trait evidence"

    return "Other evidence"


def evidence_source_link(database, identifier):
    """Generate a source URL for a known database."""

    db = str(database).strip().lower()
    item = quote(str(identifier).strip())

    if db in {"ncbi", "gene"}:
        return (
            "https://www.ncbi.nlm.nih.gov/gene/"
            f"?term={item}"
        )

    if db in {"ensembl", "ensembl plants"}:
        return (
            "https://plants.ensembl.org/Multi/Search/Results"
            f"?q={item}"
        )

    if db == "uniprot":
        return (
            f"https://www.uniprot.org/uniprotkb/{item}/entry"
        )

    if db == "interpro":
        return (
            "https://www.ebi.ac.uk/interpro/"
            f"protein/UniProt/{item}"
        )

    if db in {"pubmed", "literature"}:
        return f"https://pubmed.ncbi.nlm.nih.gov/{item}/"

    if db == "gramene":
        return f"https://www.gramene.org/search?query={item}"

    return ""


def save_evidence(
    database,
    identifier,
    description="",
    source_url="",
    record_type="database record",
    project_id=None,
    session_id=None,
):
    """Save an evidence record with its provenance."""

    database = str(database).strip()
    identifier = str(identifier).strip()

    if not database or not identifier:
        raise ValueError(
            "Database name and record identifier are required."
        )

    records = _records()

    duplicate = next(
        (
            record for record in records
            if record["database"].lower() == database.lower()
            and record["identifier"] == identifier
            and record["project_id"] == project_id
        ),
        None,
    )

    if duplicate:
        return duplicate

    if not source_url:
        source_url = evidence_source_link(
            database,
            identifier,
        )

    record = {
        "evidence_id": str(uuid4()),
        "database": database,
        "identifier": identifier,
        "description": str(description),
        "source_url": str(source_url),
        "record_type": str(record_type),
        "evidence_class": classify_evidence(
            database,
            record_type,
        ),
        "project_id": project_id,
        "session_id": session_id,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }

    records.insert(0, record)

    return record


def list_evidence(project_id=None, session_id=None, limit=100):
    """Retrieve evidence, optionally filtered by project or session."""

    records = _records()

    if project_id is not None:
        records = [
            record for record in records
            if record["project_id"] == project_id
        ]

    if session_id is not None:
        records = [
            record for record in records
            if record["session_id"] == session_id
        ]

    return records[:max(0, int(limit))]
