
"""Sequence composition and statistical analysis."""

from collections import Counter

from Bio.Seq import Seq

from core.data_loader import infer_sequence_type


def reverse_complement(sequence):
    """Return the reverse complement of a DNA or RNA sequence."""
    seq = str(sequence).upper()

    if "U" in seq and "T" not in seq:
        return str(Seq(seq).reverse_complement_rna())

    return str(Seq(seq).reverse_complement())


def nucleotide_statistics(sequence):
    seq = str(sequence).upper()
    counts = Counter(seq)
    length = len(seq)

    if length == 0:
        raise ValueError("Sequence cannot be empty.")

    canonical = sum(counts.get(base, 0) for base in "ACGTU")
    gc_count = counts.get("G", 0) + counts.get("C", 0)

    return {
        "Length": length,
        "Sequence type": infer_sequence_type(seq),
        "A count": counts.get("A", 0),
        "C count": counts.get("C", 0),
        "G count": counts.get("G", 0),
        "T count": counts.get("T", 0),
        "U count": counts.get("U", 0),
        "GC content (%)": round(gc_count / length * 100, 3),
        "AT content (%)": round(
            (counts.get("A", 0) + counts.get("T", 0)) / length * 100,
            3,
        ),
        "N count": counts.get("N", 0),
        "Ambiguous symbols": length - canonical,
    }


def protein_statistics(sequence):
    seq = str(sequence).upper().replace("*", "")
    length = len(seq)

    if length == 0:
        raise ValueError("Protein sequence cannot be empty.")

    counts = Counter(seq)
    amino_acids = "ACDEFGHIKLMNPQRSTVWY"
    valid_count = sum(counts.get(aa, 0) for aa in amino_acids)

    return {
        "Length": length,
        "Sequence type": "protein",
        "Amino acid counts": dict(counts),
        "Valid amino acids": valid_count,
        "Unknown or ambiguous residues": length - valid_count,
        "Molecular weight (Da)": round(
            float(Seq(seq).molecular_weight()),
            3,
        ),
        "Isoelectric point": None,
    }


def analyze_sequence(sequence, sequence_type=None):
    """Run sequence statistics based on sequence type."""
    seq = str(sequence).upper().replace(" ", "").replace("\n", "")

    if not seq:
        raise ValueError("Sequence cannot be empty.")

    detected = sequence_type or infer_sequence_type(seq)

    if detected.lower() in {"dna", "rna"}:
        result = nucleotide_statistics(seq)
    elif detected.lower() in {"protein", "aa"}:
        result = protein_statistics(seq)
    else:
        raise ValueError(
            "Sequence type could not be determined. "
            "Specify DNA, RNA or protein."
        )

    result["Sequence type"] = detected.upper() if detected.lower() != "protein" else "protein"
    result["Sequence"] = seq
    return result


def analyze_multiple_sequences(records):
    """Analyze a list of sequence record dictionaries."""
    results = []

    for record in records:
        sequence = record.get("sequence", "")
        sequence_type = record.get("sequence_type")

        result = analyze_sequence(sequence, sequence_type)
        result["Record ID"] = record.get("id", "Unknown")
        results.append(result)

    return results


def sliding_window_gc(sequence, window_size=100, step_size=25):
    """Calculate GC percentage across sliding windows."""
    seq = str(sequence).upper()

    if window_size <= 0 or step_size <= 0:
        raise ValueError("Window and step sizes must be positive.")

    if window_size > len(seq):
        raise ValueError("Window size exceeds sequence length.")

    results = []

    for start in range(0, len(seq) - window_size + 1, step_size):
        window = seq[start:start + window_size]
        gc = window.count("G") + window.count("C")

        results.append({
            "Start": start + 1,
            "End": start + window_size,
            "GC content (%)": round(gc / window_size * 100, 3),
        })

    return results
