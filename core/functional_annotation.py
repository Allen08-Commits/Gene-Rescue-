
from __future__ import annotations

from typing import Any


def normalize_annotation(
    source: str,
    accession: str,
    annotation: dict[str, Any]
) -> dict[str, Any]:
    """
    Convert an external database annotation into
    a consistent GeneRescue AI record.
    """

    if not source or not accession:
        raise ValueError(
            "Annotation source and accession are required."
        )

    return {
        "source": source,
        "accession": accession,
        "protein_name": annotation.get(
            "protein_name"
        ),
        "gene_name": annotation.get(
            "gene_name"
        ),
        "organism": annotation.get(
            "organism"
        ),
        "function": annotation.get(
            "function"
        ),
        "domains": annotation.get(
            "domains", []
        ),
        "go_terms": annotation.get(
            "go_terms", []
        ),
        "pathways": annotation.get(
            "pathways", []
        ),
        "evidence_codes": annotation.get(
            "evidence_codes", []
        ),
        "source_url": annotation.get(
            "source_url"
        ),
        "retrieved_at": annotation.get(
            "retrieved_at"
        ),
        "annotation_status": (
            "Retrieved database annotation"
        )
    }


def validate_annotation(
    annotation: dict[str, Any]
) -> dict[str, Any]:
    required = {
        "source",
        "accession"
    }

    missing = required - set(annotation.keys())

    if missing:
        raise ValueError(
            f"Missing annotation fields: {', '.join(sorted(missing))}"
        )

    if not annotation["source"] or not annotation["accession"]:
        raise ValueError(
            "Source and accession cannot be empty."
        )

    return annotation


def merge_annotations(
    annotations: list[dict[str, Any]]
) -> dict[str, Any]:
    """
    Combine annotations while preserving their
    individual database provenance.
    """

    validated = [
        validate_annotation(item)
        for item in annotations
    ]

    if not validated:
        return {
            "accession": None,
            "sources": [],
            "annotations": [],
            "interpretation": (
                "No external functional annotations were retrieved."
            )
        }

    accessions = {
        item["accession"]
        for item in validated
    }

    if len(accessions) > 1:
        return {
            "accession": None,
            "sources": sorted({
                item["source"] for item in validated
            }),
            "annotations": validated,
            "interpretation": (
                "Records have different accessions. "
                "They are preserved separately and must not "
                "be treated as annotations of one identical protein."
            )
        }

    return {
        "accession": next(iter(accessions)),
        "sources": sorted({
            item["source"] for item in validated
        }),
        "annotations": validated,
        "interpretation": (
            "Multiple external records are grouped by accession. "
            "Differences between database annotations should be reviewed."
        )
    }
