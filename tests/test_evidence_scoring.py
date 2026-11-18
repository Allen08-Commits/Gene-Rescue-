from services.evidence_scoring import score_evidence


def test_empty_evidence():
    result = score_evidence([])

    assert result is not None


def test_evidence_scoring():
    records = [
        {
            "database": "NCBI",
            "record_type": "gene record",
            "identifier": "GENE001",
        },
        {
            "database": "UniProt",
            "record_type": "protein record",
            "identifier": "PROTEIN001",
        },
    ]

    result = score_evidence(records)

    assert result is not None
    assert "score" in result