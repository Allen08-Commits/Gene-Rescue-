
"""Evidence coverage scoring for research records."""

EVIDENCE_CLASSES = [
    "Gene/genomic evidence",
    "Protein/function evidence",
    "Literature evidence",
    "Plant/trait evidence",
    "Other evidence",
]


def score_evidence(records):
    if not records:
        return {
            "score": 0,
            "coverage": 0,
            "represented_classes": [],
            "missing_classes": EVIDENCE_CLASSES.copy(),
            "interpretation": "No evidence records have been collected.",
        }

    represented = sorted({
        record.get("evidence_class", "Other evidence")
        for record in records
    })

    represented_expected = [
        category for category in EVIDENCE_CLASSES
        if category in represented
    ]

    missing = [
        category for category in EVIDENCE_CLASSES
        if category not in represented_expected
    ]

    coverage = len(represented_expected) / len(EVIDENCE_CLASSES)
    score = round(coverage * 100)

    if score >= 80:
        interpretation = "Broad evidence coverage. Experimental validation is still required."
    elif score >= 60:
        interpretation = "Good evidence coverage, with some evidence categories missing."
    elif score >= 40:
        interpretation = "Moderate evidence coverage. Collect additional independent evidence."
    elif score > 0:
        interpretation = "Limited evidence coverage. More supporting records are needed."
    else:
        interpretation = "No recognized evidence categories are represented."

    return {
        "score": score,
        "coverage": round(coverage * 100, 1),
        "represented_classes": represented_expected,
        "missing_classes": missing,
        "interpretation": interpretation,
    }
