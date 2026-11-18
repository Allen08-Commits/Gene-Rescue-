
"""Pairwise biological sequence comparison."""

from Bio.Align import PairwiseAligner


def _aligner():
    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score = 2
    aligner.mismatch_score = -1
    aligner.open_gap_score = -5
    aligner.extend_gap_score = -1
    return aligner


def calculate_sequence_identity(sequence_a, sequence_b):
    """Return aligned identity percentage for two sequences."""
    a = str(sequence_a).upper()
    b = str(sequence_b).upper()

    if not a or not b:
        raise ValueError("Both sequences must be non-empty.")

    alignment = _aligner().align(a, b)[0]

    aligned_a = alignment[0]
    aligned_b = alignment[1]

    comparable = 0
    identical = 0

    for base_a, base_b in zip(aligned_a, aligned_b):
        if base_a == "-" or base_b == "-":
            continue

        comparable += 1

        if base_a == base_b:
            identical += 1

    identity = (
        identical / comparable * 100
        if comparable else 0
    )

    return {
        "Identity (%)": round(identity, 3),
        "Identical positions": identical,
        "Compared positions": comparable,
        "Alignment score": float(alignment.score),
        "Alignment length": len(aligned_a),
        "Aligned sequence A": aligned_a,
        "Aligned sequence B": aligned_b,
    }


def compare_sequences(sequence_a, sequence_b, name_a="Sequence A",
                      name_b="Sequence B"):
    """Return a named pairwise comparison result."""
    result = calculate_sequence_identity(
        sequence_a,
        sequence_b,
    )

    result["Sequence A"] = name_a
    result["Sequence B"] = name_b
    result["Length A"] = len(sequence_a)
    result["Length B"] = len(sequence_b)

    return result
