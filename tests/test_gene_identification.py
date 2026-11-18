from core.gene_identification import identify_orfs


def test_orf_identification():
    sequence = "ATG" + ("AAA" * 10) + "TAA"

    results = identify_orfs(
        sequence,
        min_amino_acids=5,
    )

    assert len(results) > 0

    first_orf = results[0]

    assert first_orf["Length_aa"] >= 5
    assert first_orf["Strand"] in ["+", "-"]
    assert first_orf["Protein_Sequence"].startswith("M")