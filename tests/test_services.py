
import streamlit as st
import pandas as pd
import pytest

from services.session_manager import (
    create_research_session,
    list_research_sessions,
    get_research_session,
    clear_research_history,
)

from services.project_manager import (
    create_project,
    list_projects,
    get_project,
    update_project,
    delete_project,
)

from services.evidence_manager import (
    save_evidence,
    list_evidence,
    classify_evidence,
    evidence_source_link,
)

from services.evidence_scoring import score_evidence
from services.report_manager import generate_pdf_report


@pytest.fixture(autouse=True)
def clean_session_state(monkeypatch):
    """Give each test an isolated session-state dictionary."""
    monkeypatch.setattr(st, "session_state", {})


def test_create_and_retrieve_project():
    project = create_project(
        "Rice Gene Analysis",
        description="Study of candidate genes",
        organism="Oryza sativa",
        crop="Rice",
    )

    assert project["project_name"] == "Rice Gene Analysis"
    assert get_project(project["project_id"]) is not None
    assert len(list_projects()) == 1


def test_update_project():
    project = create_project("Original Project")

    updated = update_project(
        project["project_id"],
        {"project_name": "Updated Project"},
    )

    assert updated["project_name"] == "Updated Project"


def test_delete_project():
    project = create_project("Temporary Project")

    assert delete_project(project["project_id"]) is True
    assert get_project(project["project_id"]) is None


def test_create_research_session():
    record = create_research_session(
        tool_name="Sequence Analysis",
        session_title="Rice sequence examination",
        input_summary="Uploaded sequence",
        result_summary="Sequence analyzed",
    )

    assert record["tool_name"] == "Sequence Analysis"
    assert get_research_session(record["session_id"]) is not None
    assert len(list_research_sessions()) == 1


def test_clear_research_history():
    create_research_session("Sequence Analysis", "Test session")
    clear_research_history()

    assert list_research_sessions() == []


def test_save_and_retrieve_evidence():
    record = save_evidence(
        database="UniProt",
        identifier="P12345",
        description="Protein record",
        record_type="protein",
        source_url="https://www.uniprot.org/",
    )

    assert record["identifier"] == "P12345"
    assert record["evidence_class"] == "Protein/function evidence"
    assert len(list_evidence()) == 1


def test_duplicate_evidence_is_not_added_twice():
    first = save_evidence(
        database="UniProt",
        identifier="P12345",
        record_type="protein",
    )

    second = save_evidence(
        database="UniProt",
        identifier="P12345",
        record_type="protein",
    )

    assert first["evidence_id"] == second["evidence_id"]
    assert len(list_evidence()) == 1


def test_evidence_classification():
    assert classify_evidence("NCBI", "gene") == "Gene/genomic evidence"
    assert classify_evidence("UniProt", "protein") == "Protein/function evidence"
    assert classify_evidence("PubMed", "article") == "Literature evidence"


def test_evidence_source_link():
    link = evidence_source_link("uniprot", "P12345")

    assert "P12345" in link
    assert link.startswith("https://")


def test_evidence_scoring():
    records = [
        {"evidence_class": "Gene/genomic evidence"},
        {"evidence_class": "Protein/function evidence"},
        {"evidence_class": "Literature evidence"},
        {"evidence_class": "Plant/trait evidence"},
        {"evidence_class": "Other evidence"},
    ]

    result = score_evidence(records)

    assert result["score"] == 100
    assert result["coverage"] == 100.0
    assert len(result["missing_classes"]) == 0


def test_empty_evidence_scoring():
    result = score_evidence([])

    assert result["score"] == 0
    assert result["coverage"] == 0


def test_pdf_report_generation():
    results = pd.DataFrame({
        "Gene": ["GENE1", "GENE2"],
        "Organism": ["Rice", "Wheat"],
    })

    pdf = generate_pdf_report(
        title="GeneRescue AI Research Report",
        sections=[
            {
                "heading": "Study Information",
                "content": "Test research report",
            },
            {
                "heading": "Gene Results",
                "dataframe": results,
            },
        ],
    )

    content = pdf.getvalue()

    assert content.startswith(b"%PDF")
    assert len(content) > 500
