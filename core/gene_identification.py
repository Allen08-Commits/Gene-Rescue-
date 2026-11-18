
from __future__ import annotations

from Bio.Seq import Seq

from core.data_loader import (
    DataValidationError,
    infer_sequence_type
)


START_CODONS = {"ATG"}
STOP_CODONS = {"TAA", "TAG", "TGA"}


def identify_orfs(
    sequence: str,
    min_amino_acids: int = 30,
    nested: bool = False
) -> list[dict]:
    sequence = "".join(sequence.split()).upper()

    if not sequence:
        raise DataValidationError(
            "Input sequence is empty."
        )

    if infer_sequence_type(sequence)["type"] != "DNA":
        raise DataValidationError(
            "ORF discovery requires a DNA sequence."
        )

    if min_amino_acids < 1:
        raise ValueError(
            "Minimum amino acid length must be positive."
        )

    results = []
    sequence_length = len(sequence)

    strands = [
        ("+", sequence),
        ("-", str(Seq(sequence).reverse_complement()))
    ]

    for strand, oriented_sequence in strands:

        for frame in range(3):
            frame_sequence = oriented_sequence[frame:]

            starts = []

            for position in range(
                0,
                len(frame_sequence) - 2,
                3
            ):
                codon = frame_sequence[position:position + 3]

                if codon in START_CODONS:
                    starts.append(position)

                elif codon in STOP_CODONS:

                    eligible = [
                        start for start in starts
                        if start < position
                    ]

                    if not nested and eligible:
                        eligible = eligible[:1]

                    for start in eligible:
                        coding_sequence = frame_sequence[
                            start:position + 3
                        ]

                        amino_acids = str(
                            Seq(coding_sequence).translate(
                                to_stop=True
                            )
                        )

                        if len(amino_acids) < min_amino_acids:
                            continue

                        oriented_start = frame + start
                        oriented_end = frame + position + 3

                        if strand == "+":
                            genomic_start = oriented_start + 1
                            genomic_end = oriented_end
                        else:
                            genomic_start = (
                                sequence_length - oriented_end + 1
                            )
                            genomic_end = (
                                sequence_length - oriented_start
                            )

                        results.append({
                            "strand": strand,
                            "frame": frame + 1,
                            "start": genomic_start,
                            "end": genomic_end,
                            "nucleotide_length": len(coding_sequence),
                            "amino_acid_length": len(amino_acids),
                            "start_codon": "ATG",
                            "stop_codon": codon,
                            "protein_sequence": amino_acids,
                            "prediction_type": "Computational ORF candidate"
                        })

                    starts = []

    results.sort(
        key=lambda item: (
            item["amino_acid_length"],
            item["start"]
        ),
        reverse=True
    )

    for index, result in enumerate(results, start=1):
        result["ORF_ID"] = f"ORF_{index:04d}"

    return results


def identify_multiple_orfs(
    records: list[dict],
    min_amino_acids: int = 30
) -> list[dict]:
    all_results = []

    for record in records:
        orfs = identify_orfs(
            record["sequence"],
            min_amino_acids=min_amino_acids
        )

        for orf in orfs:
            orf["source_sequence_id"] = record.get(
                "id", "Unknown"
            )

        all_results.extend(orfs)

    return all_results
