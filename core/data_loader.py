
"""Universal bioinformatics dataset loader."""

from io import StringIO
from pathlib import Path

import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq


class DataValidationError(ValueError):
    """Raised when an uploaded dataset cannot be validated."""


def _read_text(uploaded_file):
    if isinstance(uploaded_file, (str, Path)):
        path = Path(uploaded_file)
        if not path.exists():
            raise DataValidationError(f"File not found: {path}")
        return path.read_text(encoding="utf-8-sig")

    if isinstance(uploaded_file, bytes):
        return uploaded_file.decode("utf-8-sig")

    if hasattr(uploaded_file, "getvalue"):
        content = uploaded_file.getvalue()
    elif hasattr(uploaded_file, "read"):
        content = uploaded_file.read()
    else:
        raise DataValidationError("Unsupported file input.")

    if isinstance(content, str):
        return content

    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DataValidationError(
            "The uploaded file is not valid UTF-8 text."
        ) from exc


def infer_sequence_type(sequence):
    """Classify a sequence as DNA, RNA, protein or unknown."""
    seq = str(sequence).upper().replace(" ", "").replace("\n", "")

    if not seq:
        return "unknown"

    dna = set("ACGTNRYKMSWBDHV")
    rna = set("ACGUNRYKMSWBDHV")
    protein = set("ABCDEFGHIKLMNPQRSTVWXYZJUO*")

    chars = set(seq)

    if chars <= dna:
        return "DNA"

    if chars <= rna and "U" in chars:
        return "RNA"

    if chars <= protein:
        return "protein"

    return "unknown"


def _validate_sequence(sequence):
    seq = str(sequence).upper()
    seq = "".join(seq.split())

    if not seq:
        raise DataValidationError("An empty sequence was found.")

    if any(char.isspace() for char in seq):
        raise DataValidationError("Invalid whitespace in sequence.")

    if infer_sequence_type(seq) == "unknown":
        raise DataValidationError(
            "Sequence contains unsupported biological symbols."
        )

    return seq


def load_fasta(uploaded_file):
    """Read FASTA and return a list of sequence records."""
    text = _read_text(uploaded_file)

    if not text.lstrip().startswith(">"):
        raise DataValidationError("The file does not appear to be FASTA.")

    records = []

    try:
        for record in SeqIO.parse(StringIO(text), "fasta"):
            sequence = _validate_sequence(str(record.seq))

            records.append({
                "id": record.id,
                "description": record.description,
                "sequence": sequence,
                "sequence_type": infer_sequence_type(sequence),
                "length": len(sequence),
            })
    except Exception as exc:
        raise DataValidationError(
            f"Could not parse FASTA: {exc}"
        ) from exc

    if not records:
        raise DataValidationError("No FASTA records were found.")

    return records


def load_fastq(uploaded_file):
    """Read FASTQ records, retaining their quality scores."""
    text = _read_text(uploaded_file)
    records = []

    try:
        for record in SeqIO.parse(StringIO(text), "fastq"):
            sequence = _validate_sequence(str(record.seq))
            qualities = record.letter_annotations.get(
                "phred_quality", []
            )

            records.append({
                "id": record.id,
                "description": record.description,
                "sequence": sequence,
                "sequence_type": infer_sequence_type(sequence),
                "length": len(sequence),
                "phred_quality": list(qualities),
            })
    except Exception as exc:
        raise DataValidationError(
            f"Could not parse FASTQ: {exc}"
        ) from exc

    if not records:
        raise DataValidationError("No FASTQ records were found.")

    return records


def load_table(uploaded_file, delimiter=None):
    """Load CSV or TSV data with automatic delimiter detection."""
    text = _read_text(uploaded_file)

    if not text.strip():
        raise DataValidationError("The uploaded table is empty.")

    try:
        if delimiter:
            dataframe = pd.read_csv(StringIO(text), sep=delimiter)
        else:
            dataframe = pd.read_csv(
                StringIO(text),
                sep=None,
                engine="python",
            )
    except Exception as exc:
        raise DataValidationError(
            f"Could not read the table: {exc}"
        ) from exc

    if dataframe.empty or len(dataframe.columns) == 0:
        raise DataValidationError("No usable table data was found.")

    dataframe.columns = [
        str(column).strip() for column in dataframe.columns
    ]

    return dataframe


def load_vcf(uploaded_file):
    """Load VCF records into a normalized pandas DataFrame."""
    text = _read_text(uploaded_file)
    rows = []
    sample_names = []

    for line in text.splitlines():
        if line.startswith("##"):
            continue

        if line.startswith("#CHROM"):
            sample_names = line.lstrip("#").split("\t")
            continue

        if not line.strip() or line.startswith("#"):
            continue

        fields = line.split("\t")

        if len(fields) < 8:
            raise DataValidationError(
                "A VCF record contains fewer than eight columns."
            )

        rows.append({
            "CHROM": fields[0],
            "POS": fields[1],
            "ID": fields[2],
            "REF": fields[3],
            "ALT": fields[4],
            "QUAL": fields[5],
            "FILTER": fields[6],
            "INFO": fields[7],
            "FORMAT": fields[8] if len(fields) > 8 else "",
            "SAMPLES": fields[9:] if len(fields) > 9 else [],
        })

    if not rows:
        raise DataValidationError("No VCF variant records were found.")

    dataframe = pd.DataFrame(rows)
    dataframe.attrs["sample_columns"] = sample_names[9:]
    return dataframe


def load_dataset(uploaded_file, file_name=None):
    """Identify and load a supported biological dataset."""
    name = file_name or getattr(uploaded_file, "name", "")
    suffix = Path(str(name)).suffix.lower()

    if suffix in {".fa", ".fasta", ".fna", ".faa"}:
        return {
            "format": "FASTA",
            "data": load_fasta(uploaded_file),
        }

    if suffix in {".fq", ".fastq"}:
        return {
            "format": "FASTQ",
            "data": load_fastq(uploaded_file),
        }

    if suffix == ".vcf":
        return {
            "format": "VCF",
            "data": load_vcf(uploaded_file),
        }

    if suffix in {".csv", ".tsv", ".txt"}:
        return {
            "format": "TABLE",
            "data": load_table(uploaded_file),
        }

    text = _read_text(uploaded_file)

    if text.lstrip().startswith(">"):
        return {
            "format": "FASTA",
            "data": load_fasta(text.encode("utf-8")),
        }

    if text.lstrip().startswith("##fileformat=VCF"):
        return {
            "format": "VCF",
            "data": load_vcf(text.encode("utf-8")),
        }

    raise DataValidationError(
        "Unsupported or unrecognized file format. "
        "Upload FASTA, FASTQ, VCF, CSV, TSV or TXT."
    )
