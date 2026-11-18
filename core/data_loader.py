
from __future__ import annotations

import csv
import io
import re
from pathlib import Path
from typing import Any

import pandas as pd
from Bio import SeqIO


SUPPORTED_SEQUENCE_EXTENSIONS = {
    ".fasta", ".fa", ".fna", ".ffn", ".faa", ".fas"
}

SUPPORTED_TABLE_EXTENSIONS = {
    ".csv", ".tsv"
}

SUPPORTED_VARIANT_EXTENSIONS = {
    ".vcf"
}

DNA_ALPHABET = set("ACGTNRYSWKMBDHV")
RNA_ALPHABET = set("ACGUNRYSWKMBDHV")
PROTEIN_ALPHABET = set(
    "ABCDEFGHIKLMNPQRSTVWXYZJUO*"
)


class DataValidationError(ValueError):
    """Raised when uploaded biological data is invalid."""


def _decode_content(content: bytes | str) -> str:
    if isinstance(content, bytes):
        try:
            return content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise DataValidationError(
                "The uploaded file must use UTF-8 text encoding."
            ) from exc

    if isinstance(content, str):
        return content.lstrip("\ufeff")

    raise DataValidationError("Unsupported file content.")


def infer_sequence_type(sequence: str) -> dict[str, Any]:
    """
    Infer DNA, RNA or protein from its alphabet.

    Ambiguous sequences are explicitly marked as uncertain.
    This is alphabet-based inference, not biological identification.
    """
    sequence = re.sub(r"\s+", "", sequence).upper()

    if not sequence:
        raise DataValidationError("Sequence is empty.")

    if any(char.isdigit() for char in sequence):
        raise DataValidationError(
            "Sequence contains numeric characters."
        )

    symbols = set(sequence)

    if symbols.issubset(DNA_ALPHABET):
        if "U" in symbols:
            raise DataValidationError(
                "Invalid DNA alphabet."
            )

        if symbols.issubset({"A", "C", "G", "T"}):
            return {
                "type": "DNA",
                "confidence": "high",
                "ambiguous": False
            }

        return {
            "type": "DNA",
            "confidence": "moderate",
            "ambiguous": True
        }

    if symbols.issubset(RNA_ALPHABET):
        if "T" not in symbols and "U" in symbols:
            return {
                "type": "RNA",
                "confidence": "high",
                "ambiguous": False
            }

        if "T" in symbols and "U" in symbols:
            raise DataValidationError(
                "Sequence contains both T and U. "
                "Specify the correct biological sequence."
            )

    if symbols.issubset(PROTEIN_ALPHABET):
        return {
            "type": "Protein",
            "confidence": "moderate",
            "ambiguous": False
        }

    invalid = sorted(symbols - DNA_ALPHABET - RNA_ALPHABET - PROTEIN_ALPHABET)

    raise DataValidationError(
        f"Unsupported sequence symbols: {', '.join(invalid)}"
    )


def load_fasta(content: bytes | str) -> list[dict[str, Any]]:
    text = _decode_content(content)

    if not text.strip().startswith(">"):
        raise DataValidationError(
            "FASTA file must begin with a header starting with '>'."
        )

    try:
        records = list(SeqIO.parse(io.StringIO(text), "fasta"))
    except Exception as exc:
        raise DataValidationError(
            f"Unable to parse FASTA file: {exc}"
        ) from exc

    if not records:
        raise DataValidationError(
            "No valid FASTA records were found."
        )

    output = []

    for record in records:
        sequence = str(record.seq).upper()

        if not sequence:
            raise DataValidationError(
                f"Sequence '{record.id}' is empty."
            )

        sequence_type = infer_sequence_type(sequence)

        output.append({
            "id": record.id,
            "description": record.description,
            "sequence": sequence,
            "length": len(sequence),
            "sequence_type": sequence_type["type"],
            "type_confidence": sequence_type["confidence"],
            "ambiguous": sequence_type["ambiguous"]
        })

    return output


def load_table(
    content: bytes | str,
    delimiter: str | None = None
) -> pd.DataFrame:
    text = _decode_content(content)

    if not text.strip():
        raise DataValidationError("The uploaded table is empty.")

    if delimiter is None:
        try:
            delimiter = csv.Sniffer().sniff(
                text[:10000],
                delimiters=",\t;"
            ).delimiter
        except csv.Error:
            raise DataValidationError(
                "Could not identify the table delimiter. "
                "Please provide a CSV or TSV file."
            )

    try:
        dataframe = pd.read_csv(
            io.StringIO(text),
            sep=delimiter,
            dtype=str,
            keep_default_na=False
        )
    except Exception as exc:
        raise DataValidationError(
            f"Unable to read table: {exc}"
        ) from exc

    if dataframe.empty or len(dataframe.columns) == 0:
        raise DataValidationError(
            "The uploaded table contains no usable data."
        )

    dataframe.columns = [
        str(column).strip() for column in dataframe.columns
    ]

    if any(not column for column in dataframe.columns):
        raise DataValidationError(
            "Every column must have a valid name."
        )

    return dataframe


def load_vcf(content: bytes | str) -> pd.DataFrame:
    text = _decode_content(content)

    columns = [
        "CHROM", "POS", "ID", "REF", "ALT",
        "QUAL", "FILTER", "INFO"
    ]

    rows = []

    for line_number, line in enumerate(
        text.splitlines(), start=1
    ):
        if not line or line.startswith("##"):
            continue

        if line.startswith("#CHROM"):
            continue

        if line.startswith("#"):
            continue

        fields = line.split("\t")

        if len(fields) < 8:
            raise DataValidationError(
                f"Malformed VCF record at line {line_number}."
            )

        row = dict(zip(columns, fields[:8]))

        try:
            position = int(row["POS"])
        except ValueError as exc:
            raise DataValidationError(
                f"Invalid VCF position at line {line_number}."
            ) from exc

        if position < 1:
            raise DataValidationError(
                f"VCF positions must be positive at line {line_number}."
            )

        if not row["REF"] or not row["ALT"]:
            raise DataValidationError(
                f"Missing REF or ALT allele at line {line_number}."
            )

        rows.append(row)

    if not rows:
        raise DataValidationError(
            "No VCF variant records were found."
        )

    dataframe = pd.DataFrame(rows)

    dataframe["POS"] = pd.to_numeric(
        dataframe["POS"],
        errors="raise"
    ).astype("int64")

    return dataframe


def load_dataset(
    filename: str,
    content: bytes | str
) -> dict[str, Any]:
    extension = Path(filename).suffix.lower()

    if extension in SUPPORTED_SEQUENCE_EXTENSIONS:
        return {
            "format": "FASTA",
            "data": load_fasta(content),
            "record_count": len(load_fasta(content))
        }

    if extension in SUPPORTED_TABLE_EXTENSIONS:
        delimiter = "\t" if extension == ".tsv" else ","
        dataframe = load_table(
            content,
            delimiter=delimiter
        )

        return {
            "format": extension[1:].upper(),
            "data": dataframe,
            "record_count": len(dataframe)
        }

    if extension in SUPPORTED_VARIANT_EXTENSIONS:
        dataframe = load_vcf(content)

        return {
            "format": "VCF",
            "data": dataframe,
            "record_count": len(dataframe)
        }

    raise DataValidationError(
        f"Unsupported file format: {extension or 'unknown'}. "
        "Supported formats: FASTA, CSV, TSV and VCF."
    )
