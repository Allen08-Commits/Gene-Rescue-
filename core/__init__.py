
"""GeneRescue AI core bioinformatics modules."""

from core.data_loader import (
    DataValidationError,
    load_dataset,
    load_fasta,
    load_table,
    load_vcf,
    infer_sequence_type,
)

from core.sequence_analysis import (
    analyze_sequence,
    analyze_multiple_sequences,
    nucleotide_statistics,
    protein_statistics,
    sliding_window_gc,
    reverse_complement,
)

from core.sequence_quality import (
    assess_sequence_quality,
    composition_screen,
)

from core.sequence_comparison import (
    compare_sequences,
    calculate_sequence_identity,
)

from core.gene_identification import identify_orfs

from core.variant_analysis import (
    analyze_variants,
    summarize_variants,
    analyze_variant_record,
)

from core.functional_annotation import (
    normalize_annotation,
    merge_annotations,
)

__all__ = [
    "DataValidationError",
    "load_dataset",
    "load_fasta",
    "load_table",
    "load_vcf",
    "infer_sequence_type",
    "analyze_sequence",
    "analyze_multiple_sequences",
    "nucleotide_statistics",
    "protein_statistics",
    "sliding_window_gc",
    "reverse_complement",
    "assess_sequence_quality",
    "composition_screen",
    "compare_sequences",
    "calculate_sequence_identity",
    "identify_orfs",
    "analyze_variants",
    "summarize_variants",
    "analyze_variant_record",
    "normalize_annotation",
    "merge_annotations",
]
