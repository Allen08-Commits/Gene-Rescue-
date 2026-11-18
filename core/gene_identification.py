
"""Open reading frame identification in DNA sequences."""

from Bio.Seq import Seq


START_CODONS = {"ATG"}
STOP_CODONS = {"TAA", "TAG", "TGA"}


def identify_orfs(sequence, min_amino_acids=30, nested=False):
    """
    Identify candidate ORFs on both DNA strands.

    Coordinates are 1-based and inclusive relative to the
    original input sequence.
    """
    dna = str(sequence).upper().replace(" ", "").replace("\n", "")

    if not dna:
        raise ValueError("DNA sequence cannot be empty.")

    if set(dna) - set("ACGTN"):
        raise ValueError("ORF identification requires a DNA sequence.")

    if min_amino_acids < 1:
        raise ValueError("Minimum amino acid length must be positive.")

    if "N" in dna:
        # ORFs spanning ambiguous bases may be unreliable.
        pass

    results = []
    strands = [
        ("+", dna),
        ("-", str(Seq(dna).reverse_complement())),
    ]

    for strand, oriented_sequence in strands:
        for frame in range(3):
            active_starts = []

            for position in range(frame, len(oriented_sequence) - 2, 3):
                codon = oriented_sequence[position:position + 3]

                if codon in START_CODONS:
                    active_starts.append(position)

                if codon in STOP_CODONS:
                    starts_to_report = (
                        active_starts if nested else active_starts[:1]
                    )

                    for start in starts_to_report:
                        coding_nt = position + 3 - start
                        amino_acids = coding_nt // 3 - 1

                        if amino_acids < min_amino_acids:
                            continue

                        coding_sequence = oriented_sequence[
                            start:position + 3
                        ]

                        protein = str(
                            Seq(coding_sequence).translate(
                                to_stop=True
                            )
                        )

                        if strand == "+":
                            original_start = start + 1
                            original_end = position + 3
                        else:
                            original_start = (
                                len(dna) - (position + 3) + 1
                            )
                            original_end = len(dna) - start

                        results.append({
                            "ORF_ID": f"ORF_{len(results) + 1}",
                            "Strand": strand,
                            "Frame": frame + 1,
                            "Start": original_start,
                            "End": original_end,
                            "Length_nt": coding_nt,
                            "Length_aa": len(protein),
                            "Protein_Sequence": protein,
                            "Coding_Sequence": coding_sequence,
                        })

                    active_starts = []

    results.sort(
        key=lambda item: (
            item["Start"],
            item["End"],
            item["Strand"],
        )
    )

    return results
