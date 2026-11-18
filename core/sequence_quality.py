
"""Sequence quality and composition screening."""

from collections import Counter


def assess_sequence_quality(sequence, phred_quality=None):
    """
    Assess sequence quality.

    Phred metrics are calculated only when actual quality scores
    are supplied, such as those parsed from FASTQ.
    """
    seq = str(sequence).upper()
    length = len(seq)

    if not length:
        raise ValueError("Sequence cannot be empty.")

    ambiguous = sum(
        1 for base in seq if base not in "ACGTU"
    )

    result = {
        "Length": length,
        "Ambiguous bases": ambiguous,
        "Ambiguous percentage": round(
            ambiguous / length * 100, 3
        ),
        "GC content (%)": round(
            (seq.count("G") + seq.count("C")) / length * 100,
            3,
        ),
        "Phred quality available": phred_quality is not None,
    }

    if phred_quality is not None:
        scores = [float(score) for score in phred_quality]

        if len(scores) != length:
            raise ValueError(
                "Phred score count must match sequence length."
            )

        if any(score < 0 for score in scores):
            raise ValueError("Phred scores cannot be negative.")

        result.update({
            "Mean Phred score": round(
                sum(scores) / len(scores), 3
            ),
            "Minimum Phred score": min(scores),
            "Maximum Phred score": max(scores),
            "Bases Q20 or higher": sum(
                score >= 20 for score in scores
            ),
            "Bases Q30 or higher": sum(
                score >= 30 for score in scores
            ),
            "Q20 percentage": round(
                sum(score >= 20 for score in scores) / length * 100,
                3,
            ),
            "Q30 percentage": round(
                sum(score >= 30 for score in scores) / length * 100,
                3,
            ),
        })

    return result


def composition_screen(sequence):
    """Screen sequence composition without claiming read quality."""
    seq = str(sequence).upper()
    length = len(seq)

    if not length:
        raise ValueError("Sequence cannot be empty.")

    counts = Counter(seq)
    gc = counts.get("G", 0) + counts.get("C", 0)
    ambiguous = sum(
        count for base, count in counts.items()
        if base not in "ACGTU"
    )

    return {
        "Length": length,
        "GC content (%)": round(gc / length * 100, 3),
        "Ambiguous percentage": round(
            ambiguous / length * 100, 3
        ),
        "Base composition (%)": {
            base: round(counts.get(base, 0) / length * 100, 3)
            for base in "ACGTU"
        },
        "Interpretation": (
            "Composition screening only. This is not a substitute "
            "for FASTQ Phred quality assessment."
        ),
    }
