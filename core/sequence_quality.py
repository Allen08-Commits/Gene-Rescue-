
from __future__ import annotations

from typing import Any

from core.sequence_analysis import analyze_sequence


def assess_sequence_quality(
    sequence: str
) -> dict[str, Any]:
    statistics = analyze_sequence(sequence)

    sequence_type = statistics["sequence_type"]

    if sequence_type == "Protein":
        return {
            "sequence_type": sequence_type,
            "status": "Composition screening only",
            "length": statistics["length"],
            "note": (
                "This assessment does not establish protein "
                "folding quality or experimental integrity."
            )
        }

    length = statistics["length"]
    ambiguous = statistics["ambiguous_bases"]

    ambiguity_percent = (
        ambiguous / length * 100
    )

    flags = []

    if length < 100:
        flags.append(
            "Short sequence: downstream analysis may be limited."
        )

    if ambiguity_percent > 5:
        flags.append(
            "High proportion of ambiguous nucleotide symbols."
        )

    if statistics["GC_percent"] < 20:
        flags.append(
            "Low GC composition relative to the screening threshold."
        )

    if statistics["GC_percent"] > 80:
        flags.append(
            "High GC composition relative to the screening threshold."
        )

    if ambiguity_percent == 0 and length >= 100:
        status = "No basic composition warning"
    elif ambiguity_percent <= 5:
        status = "Review recommended"
    else:
        status = "High ambiguity detected"

    return {
        "sequence_type": sequence_type,
        "length": length,
        "ambiguity_count": ambiguous,
        "ambiguity_percent": round(
            ambiguity_percent, 3
        ),
        "GC_percent": statistics["GC_percent"],
        "screening_status": status,
        "flags": flags,
        "interpretation": (
            "This is a basic composition screen, not a "
            "Phred-based sequencing quality assessment."
        )
    }
