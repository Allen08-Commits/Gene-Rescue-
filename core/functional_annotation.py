
"""Functional annotation normalization and integration."""

import pandas as pd


def normalize_annotation(record, source="Unknown"):
    """Convert an annotation record into a consistent structure."""
    if not isinstance(record, dict):
        raise TypeError("Annotation record must be a dictionary.")

    return {
        "Source": source,
        "Identifier": (
            record.get("accession")
            or record.get("id")
            or record.get("identifier")
            or record.get("gene_id")
            or ""
        ),
        "Name": (
            record.get("protein_name")
            or record.get("name")
            or record.get("description")
            or record.get("gene_name")
            or ""
        ),
        "Organism": (
            record.get("organism")
            or record.get("species")
            or ""
        ),
        "Function": (
            record.get("function")
            or record.get("annotation")
            or record.get("description")
            or ""
        ),
        "Evidence": (
            record.get("evidence")
            or record.get("evidence_type")
            or ""
        ),
        "Source URL": (
            record.get("source_url")
            or record.get("url")
            or ""
        ),
        "Raw record": record,
    }


def merge_annotations(annotation_groups):
    """
    Combine annotation groups while preserving their source.

    Expected input:
    [
        {"source": "UniProt", "records": [...]},
        {"source": "InterPro", "records": [...]}
    ]
    """
    normalized = []

    for group in annotation_groups:
        source = group.get("source", "Unknown")
        records = group.get("records", [])

        for record in records:
            normalized.append(
                normalize_annotation(record, source=source)
            )

    if not normalized:
        return pd.DataFrame(columns=[
            "Source",
            "Identifier",
            "Name",
            "Organism",
            "Function",
            "Evidence",
            "Source URL",
            "Raw record",
        ])

    return pd.DataFrame(normalized)
