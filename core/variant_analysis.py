
"""Variant record normalization and summary analysis."""

import pandas as pd


def _classify_variant(ref, alt):
    ref = str(ref).upper()
    alt = str(alt).upper()

    if alt in {"", ".", "*"} or ref in {"", "."}:
        return "Unknown"

    if "," in alt:
        return "Multi-allelic"

    if len(ref) == 1 and len(alt) == 1:
        return "SNP" if ref != alt else "No change"

    if len(ref) < len(alt):
        return "Insertion"

    if len(ref) > len(alt):
        return "Deletion"

    return "MNV"


def analyze_variant_record(record):
    """Normalize and classify one variant record."""
    ref = record.get("REF", record.get("ref", ""))
    alt = record.get("ALT", record.get("alt", ""))

    return {
        "Chromosome": record.get(
            "CHROM", record.get("chromosome", record.get("CHROMOSOME", ""))
        ),
        "Position": record.get(
            "POS", record.get("position", record.get("POS", ""))
        ),
        "Variant_ID": record.get(
            "ID", record.get("variant_id", "")
        ),
        "Reference": ref,
        "Alternate": alt,
        "Variant_Type": _classify_variant(ref, alt),
        "Quality": record.get("QUAL", record.get("quality", "")),
        "Filter": record.get("FILTER", record.get("filter", "")),
    }


def analyze_variants(data):
    """Analyze a VCF-derived or tabular variant DataFrame."""
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    if data.empty:
        raise ValueError("No variant records were supplied.")

    columns = {str(col).upper(): col for col in data.columns}

    ref_column = columns.get("REF") or columns.get("REFERENCE")
    alt_column = columns.get("ALT") or columns.get("ALTERNATE")

    if ref_column is None or alt_column is None:
        raise ValueError(
            "Variant data must contain REF and ALT columns "
            "(or Reference and Alternate)."
        )

    output = []

    for _, row in data.iterrows():
        record = row.to_dict()

        if ref_column != "REF":
            record["REF"] = row[ref_column]

        if alt_column != "ALT":
            record["ALT"] = row[alt_column]

        output.append(analyze_variant_record(record))

    return pd.DataFrame(output)


def summarize_variants(variants):
    """Summarize normalized variant records."""
    if not isinstance(variants, pd.DataFrame):
        variants = pd.DataFrame(variants)

    if variants.empty:
        return {
            "Total variants": 0,
            "Variant type counts": {},
        }

    if "Variant_Type" not in variants.columns:
        variants = analyze_variants(variants)

    counts = variants["Variant_Type"].value_counts().to_dict()

    return {
        "Total variants": int(len(variants)),
        "Variant type counts": {
            str(key): int(value)
            for key, value in counts.items()
        },
        "SNP count": int(counts.get("SNP", 0)),
        "Insertion count": int(counts.get("Insertion", 0)),
        "Deletion count": int(counts.get("Deletion", 0)),
        "MNV count": int(counts.get("MNV", 0)),
    }
