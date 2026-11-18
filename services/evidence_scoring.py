
"""Evidence coverage scoring."""

EVIDENCE_CLASSES = [
    "Gene/genomic evidence",
    "Protein/function evidence",
    "Literature evidence",
    "Plant/trait evidence",
    "Other evidence",
]


def score_evidence(records):
    """Calculate the breadth of evidence represented."""

    if not records:
        return {
            "score": 0,
            "coverage": 0.0,
            "represented_classes": [],
            "missing_classes": EVIDENCE_CLASSES.copy(),
            "interpretation": (
                "No evidence records have been collected."
            ),
        }

    represented = {
        record.get("evidence_class", "Other evidence")
        for record in records
    }

    present = [
        category for category in EVIDENCE_CLASSES
        if category in represented
    ]

    missing = [
        category for category in EVIDENCE_CLASSES
        if category not in represented
    ]

    coverage = len(present) / len(EVIDENCE_CLASSES) * 100
    score = round(coverage)

    if score >= 80:
        interpretation = (
            "Broad evidence coverage. Independent validation "
            "is still necessary."
        )
    elif score >= 60:
        interpretation = (
            "Good evidence coverage, with some categories missing."
        )
    elif score >= 40:
        interpretation = (
            "Moderate coverage. Additional independent evidence "
            "would strengthen the research."
        )
    elif score > 0:
        interpretation = (
            "Limited coverage. More supporting records are needed."
        )
    else:
        interpretation = "No recognized evidence categories found."

    return {
        "score": score,
        "coverage": round(coverage, 1),
        "represented_classes": present,
        "missing_classes": missing,
        "interpretation": interpretation,
    }
