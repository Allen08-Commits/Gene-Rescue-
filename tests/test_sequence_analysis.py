from core.sequence_analysis import (
    analyze_sequence,
    reverse_complement,
    nucleotide_statistics,
)


def test_dna_sequence_analysis():
    sequence = "ATGCGCAT"

    result = analyze_sequence(sequence, "DNA")

    assert result["Length"] == 8
    assert result["Sequence type"] == "DNA"
    assert 0 <= result["GC content (%)"] <= 100


def test_reverse_complement():
    assert reverse_complement("ATGC") == "GCAT"


def test_nucleotide_statistics():
    result = nucleotide_statistics("AATTGGCC")

    assert result["A"] == 2
    assert result["T"] == 2
    assert result["G"] == 2
    assert result["C"] == 2