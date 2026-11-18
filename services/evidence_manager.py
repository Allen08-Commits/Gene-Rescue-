
"""Manage evidence records collected from external databases."""
import streamlit as st
from uuid import uuid4
from datetime import datetime, timezone


def _records():
    if "research_evidence" not in st.session_state:
        st.session_state["research_evidence"] = []
    return st.session_state["research_evidence"]


def classify_evidence(database, record_type=""):
    text = f"{database} {record_type}".lower()

    if any(x in text for x in ["ncbi", "gene", "genome", "ensembl"]):
        return "Gene/genomic evidence"
    if any(x in text for x in ["uniprot", "protein", "interpro"]):
        return "Protein/function evidence"
    if any(x in text for x in ["pubmed", "publication", "article"]):
        return "Literature evidence"
    if any(x in text for x in ["gramene", "plant", "crop", "trait"]):
        return "Plant/trait evidence"
    return "Other evidence"


def save_evidence(
    database,
    identifier,
    description="",
    source_url="",
    record_type="database record",
    project_id=None,
    session_id=None,
):
    record = {
        "evidence_id": str(uuid4()),
        "database": str(database),
        "identifier": str(identifier),
        "description": str(description),
        "source_url": str(source_url),
        "record_type": str(record_type),
        "evidence_class": classify_evidence(database, record_type),
        "project_id": project_id,
        "session_id": session_id,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }

    existing = _records()
    duplicate = next(
        (
            item for item in existing
            if item["database"] == record["database"]
            and item["identifier"] == record["identifier"]
            and item["project_id"] == project_id
        ),
        None,
    )

    if duplicate:
        return duplicate

    existing.insert(0, record)
    return record


def list_evidence(project_id=None, session_id=None, limit=100):
    records = _records()

    if project_id is not None:
        records = [r for r in records if r["project_id"] == project_id]

    if session_id is not None:
        records = [r for r in records if r["session_id"] == session_id]

    return records[:max(0, int(limit))]


def evidence_source_link(database, identifier):
    database = str(database).lower()
    identifier = str(identifier).strip()

    if database in {"ncbi", "gene"}:
        return f"https://www.ncbi.nlm.nih.gov/gene/?term={identifier}"
    if database in {"ensembl", "ensembl plants"}:
        return f"https://plants.ensembl.org/Multi/Search/Results?q={identifier}"
    if database == "uniprot":
        return f"https://www.uniprot.org/uniprotkb/{identifier}/entry"
    if database == "interpro":
        return f"https://www.ebi.ac.uk/interpro/protein/UniProt/{identifier}"
    if database in {"pubmed", "literature"}:
        return f"https://pubmed.ncbi.nlm.nih.gov/{identifier}/"
    if database == "gramene":
        return f"https://www.gramene.org/search?query={identifier}"

    return ""
