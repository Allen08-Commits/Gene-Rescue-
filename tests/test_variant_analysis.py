import pandas as pd

from core.variant_analysis import (
    analyze_variants,
    summarize_variants,
)


def test_variant_analysis():
    data = pd.DataFrame({
        "CHROM": ["1", "1", "2"],
        "POS": [100, 200, 300],
        "REF": ["A", "AT", "G"],
        "ALT": ["G", "A", "T"],
    })

    result = analyze_variants(data)

    assert len(result) == 3
    assert "Variant_Type" in result.columns


def test_variant_summary():
    data = pd.DataFrame({
        "CHROM": ["1", "1"],
        "POS": [100, 200],
        "REF": ["A", "C"],
        "ALT": ["G", "T"],
    })

    result = analyze_variants(data)
    summary = summarize_variants(result)

    assert summary is not None