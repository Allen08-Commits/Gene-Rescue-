
from __future__ import annotations

from Bio.Align import PairwiseAligner

from core.data_loader import (
    DataValidationError,
    infer_sequence_type
)


def compare_sequences(
    sequence_a: str,
    sequence_b: str,
    mode: str = "global"
) -> dict:
    sequence_a = "".join(sequence_a.split()).upper()
    sequence_b = "".join(sequence_b.split()).upper()

    if not sequence_a or not sequence_b:
        raise DataValidationError(
            "Both sequences are required."
        )

    type_a = infer_sequence_type(sequence_a)["type"]
    type_b = infer_sequence_type(sequence_b)["type"]

    if type_a != type_b:
        raise DataValidationError(
            "Sequences must belong to the same inferred sequence type."
        )

    if mode not in {"global", "local"}:
        raise ValueError(
            "Mode must be 'global' or 'local'."
        )

    aligner = PairwiseAligner()

    aligner.mode = mode
    aligner.match_score = 2
    aligner.mismatch_score = -1
    aligner.open_gap_score = -5
    aligner.extend_gap_score = -0.5

    alignments = aligner.align(
        sequence_a,
        sequence_b
    )

    if len(alignments) == 0:
        raise DataValidationError(
            "No alignment could be generated."
        )

    best = alignments[0]

    aligned_a, aligned_b = best.aligned

    aligned_positions = 0
    matches = 0

    for (start_a, end_a), (start_b, end_b) in zip(
        aligned_a, aligned_b
    ):
        segment_a = sequence_a[start_a:end_a]
        segment_b = sequence_b[start_b:end_b]

        for base_a, base_b in zip(segment_a, segment_b):
            aligned_positions += 1

            if base_a == base_b:
                matches += 1

    identity = (
        matches / aligned_positions * 100
        if aligned_positions else 0
    )

    return {
        "sequence_type": type_a,
        "alignment_mode": mode,
        "alignment_score": float(best.score),
        "aligned_positions": aligned_positions,
        "identical_positions": matches,
        "percent_identity": round(identity, 3),
        "alignment_count_reported": len(alignments),
        "interpretation": (
            "Pairwise alignment describes sequence similarity. "
            "It does not independently establish biological "
            "homology, orthology or shared function."
        )
    }
..