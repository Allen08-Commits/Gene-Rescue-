
from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd

from core.data_loader import DataValidationError


VALID_ALLELES = set("ACGTN")


def classify_variant(
    reference: str,
    alternate: str
) -> str:
    reference = reference.upper().strip()
    alternate = alternate.upper().strip()

    if not reference or not alternate:
        raise DataValidationError(
            "Reference and alternate alleles are required."
        )

    if reference == alternate:
        return "No change"

    if reference.startswith("<") or alternate.startswith("<"):
        return "Symbolic variant"

    if any(base not in VALID_ALLELES for base in reference):
        raise DataValidationError(
            "Reference allele contains unsupported symbols."
        )

    if any(base not in VALID_ALLELES for base in alternate):
        raise DataValidationError(
            "Alternate allele contains unsupported symbols."
        )

    if len(reference) == 1 and len(alternate) == 1:
        return "SNP"

    if len(reference) < len(alternate):
        return "Insertion"

    if len(reference) > len(alternate):
        return "Deletion"

    return "MNV"


def analyze_variant_record(
    record: dict[str, Any]
) -> dict[str, Any]:
    reference = str(record.get("REF", "")).upper()
    alternate = str(record.get("ALT", "")).upper()

    position = record.get("POS")

    if position is None:
        raise DataValidationError(
            "Variant position is missing."
        )

    try:
        position = int(position)
    except (ValueError, TypeError) as exc:
        raise DataValidationError(
            "Variant position must be an integer."
        ) from exc

    if position < 1:
        raise DataValidationError(
            "Variant position must be positive."
        )

    if "," in alternate:
        alternate_alleles = alternate.split(",")

        types = [
            classify_variant(reference, allele)
            for allele in alternate_alleles
        ]

        variant_type = (
            types[0]
            if len(set(types)) == 1
            else "Mixed multiallelic"
        )
    else:
        alternate_alleles = [alternate]
        variant_type = classify_variant(
            reference,
            alternate
        )

    return {
        "CHROM": record.get("CHROM", ""),
        "POS": position,
        "ID": record.get("ID", "."),
        "REF": reference,
        "ALT": alternate,
        "Variant_Type": variant_type,
        "Allele_Change": f"{reference}>{alternate}",
        "QUAL": record.get("QUAL", "."),
        "FILTER": record.get("FILTER", "."),
        "Interpretation": (
            "Variant classification only. Reference-based "
            "functional annotation has not been performed."
        )
    }


def analyze_variants(
    dataframe: pd.DataFrame
) -> pd.DataFrame:
    required = {"POS", "REF", "ALT"}

    missing = required - set(dataframe.columns)

    if missing:
        raise DataValidationError(
            f"Missing required variant columns: {', '.join(sorted(missing))}"
        )

    results = []

    for _, row in dataframe.iterrows():
        results.append(
            analyze_variant_record(row.to_dict())
        )

    return pd.DataFrame(results)


def summarize_variants(
    dataframe: pd.DataFrame
) -> dict[str, Any]:
    if "Variant_Type" not in dataframe.columns:
        raise DataValidationError(
            "Variant_Type column is missing. "
            "Run variant analysis first."
        )

    counts = Counter(
        dataframe["Variant_Type"].fillna("Unknown")
    )

    return {
        "total_variants": int(len(dataframe)),
        "variant_type_counts": dict(counts),
        "unique_chromosomes": (
            int(dataframe["CHROM"].nunique())
            if "CHROM" in dataframe.columns
            else None
        )
    }
