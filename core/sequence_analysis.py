
from __future__ import annotations

from collections import Counter
from typing import Any

from Bio.SeqUtils.ProtParam import ProteinAnalysis

from core.data_loader import (
    DataValidationError,
    infer_sequence_type
)


def _clean_sequence(sequence: str) -> str:
    cleaned = "".join(sequence.split()).upper()

    if not cleaned:
        raise DataValidationError("Sequence is empty.")

    return cleaned


def nucleotide_statistics(sequence: str) -> dict[str, Any]:
    sequence = _clean_sequence(sequence)

    sequence_type = infer_sequence_type(sequence)["type"]

    if sequence_type not in {"DNA", "RNA"}:
        raise DataValidationError(
            "Nucleotide statistics require DNA or RNA."
        )

    counts = Counter(sequence)

    a = counts.get("A", 0)
    c = counts.get("C", 0)
    g = counts.get("G", 0)
    t_or_u = counts.get("T", 0) + counts.get("U", 0)
    ambiguous = len(sequence) - (a + c + g + t_or_u)

    gc = g + c
    at = a + t_or_u

    gc_percent = (
        gc / len(sequence) * 100
    )

    at_percent = (
        at / len(sequence) * 100
    )

    gc_skew = (
        (g - c) / gc if gc else None
    )

    return {
        "sequence_type": sequence_type,
        "length": len(sequence),
        "A": a,
        "C": c,
        "G": g,
        "T_or_U": t_or_u,
        "ambiguous_bases": ambiguous,
        "GC_count": gc,
        "AT_count": at,
        "GC_percent": round(gc_percent, 3),
        "AT_percent": round(at_percent, 3),
        "GC_skew": (
            round(gc_skew, 5)
            if gc_skew is not None else None
        ),
        "base_frequencies": {
            base: round(count / len(sequence), 5)
            for base, count in counts.items()
        }
    }


def protein_statistics(sequence: str) -> dict[str, Any]:
    sequence = _clean_sequence(sequence)

    sequence_type = infer_sequence_type(sequence)["type"]

    if sequence_type != "Protein":
        raise DataValidationError(
            "Protein statistics require a protein sequence."
        )

    if "*" in sequence:
        sequence = sequence.rstrip("*")

    if "*" in sequence:
        raise DataValidationError(
            "Internal stop symbols are not valid for this protein analysis."
        )

    try:
        analysis = ProteinAnalysis(sequence)

        return {
            "sequence_type": "Protein",
            "length": len(sequence),
            "molecular_weight_Da": round(
                analysis.molecular_weight(), 3
            ),
            "isoelectric_point": round(
                analysis.isoelectric_point(), 3
            ),
            "instability_index": round(
                analysis.instability_index(), 3
            ),
            "gravy": round(
                analysis.gravy(), 4
            ),
            "amino_acid_composition": {
                key: round(value, 5)
                for key, value in analysis.get_amino_acids_percent().items()
            }
        }

    except Exception as exc:
        raise DataValidationError(
            f"Unable to calculate protein properties: {exc}"
        ) from exc


def analyze_sequence(sequence: str) -> dict[str, Any]:
    sequence = _clean_sequence(sequence)

    sequence_type = infer_sequence_type(sequence)["type"]

    if sequence_type in {"DNA", "RNA"}:
        return nucleotide_statistics(sequence)

    if sequence_type == "Protein":
        return protein_statistics(sequence)

    raise DataValidationError(
        "Unsupported biological sequence."
    )


def analyze_multiple_sequences(
    records: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    results = []

    for record in records:
        result = analyze_sequence(record["sequence"])

        results.append({
            "id": record.get("id", "Sequence"),
            "description": record.get("description", ""),
            **result
        })

    return results


def sliding_window_gc(
    sequence: str,
    window_size: int = 100,
    step_size: int = 25
) -> list[dict[str, Any]]:
    sequence = _clean_sequence(sequence)

    if infer_sequence_type(sequence)["type"] not in {"DNA", "RNA"}:
        raise DataValidationError(
            "Sliding-window GC analysis requires DNA or RNA."
        )

    if window_size < 1 or step_size < 1:
        raise ValueError(
            "Window and step sizes must be positive."
        )

    if window_size > len(sequence):
        raise ValueError(
            "Window size cannot exceed sequence length."
        )

    results = []

    for start in range(
        0,
        len(sequence) - window_size + 1,
        step_size
    ):
        fragment = sequence[start:start + window_size]

        valid = sum(
            base in "ACGTU" for base in fragment
        )

        gc = sum(
            base in "GC" for base in fragment
        )

        results.append({
            "start": start + 1,
            "end": start + window_size,
            "GC_percent": (
                round(gc / valid * 100, 3)
                if valid else None
            )
        })

    return results


def reverse_complement(sequence: str) -> str:
    sequence = _clean_sequence(sequence)

    sequence_type = infer_sequence_type(sequence)["type"]

    if sequence_type == "DNA":
        return sequence.translate(
            str.maketrans(
                "ACGTNRYSWKMBDHV",
                "TGCANYRSWMKVHDB"
            )
        )[::-1]

    if sequence_type == "RNA":
        return sequence.translate(
            str.maketrans(
                "ACGUNRYSWKMBDHV",
                "UGCAN YRSWMKVHDB".replace(" ", "")
            )
        )[::-1]

    raise DataValidationError(
        "Reverse complement requires a DNA or RNA sequence."
    )
