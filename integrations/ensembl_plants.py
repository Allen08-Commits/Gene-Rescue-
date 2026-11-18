
"""Ensembl Plants integration for GeneRescue AI."""

from integrations import (
    request_json,
    request_text,
    provenance,
)

BASE_URL = "https://rest.ensembl.org"


def _get(path, params=None):
    endpoint = BASE_URL + path

    data = request_json(
        endpoint,
        params=params,
        headers={"Accept": "application/json"},
    )

    return data, endpoint


def search_plant_genes(query, species="oryza_sativa"):
    """Search Ensembl Plants for gene symbols or external names."""
    if not query.strip() or not species.strip():
        raise ValueError("Gene query and species are required.")

    endpoint = (
        f"{BASE_URL}/xrefs/symbol/"
        f"{species.strip()}/{query.strip()}"
    )

    params = {"object_type": "gene"}

    records = request_json(
        endpoint,
        params=params,
        headers={"Accept": "application/json"},
    )

    return {
        "database": "Ensembl Plants",
        "query": query,
        "species": species,
        "records": records,
        "count": len(records) if isinstance(records, list) else 0,
        "provenance": provenance(
            "Ensembl Plants",
            endpoint,
            params,
        ),
    }


def lookup_gene(identifier, expand=True):
    """Retrieve a gene record by Ensembl stable ID."""
    if not identifier.strip():
        raise ValueError("Ensembl identifier is required.")

    params = {"expand": int(bool(expand))}
    data, endpoint = _get(
        f"/lookup/id/{identifier.strip()}",
        params,
    )

    return {
        "record": data,
        "provenance": provenance(
            "Ensembl Plants", endpoint, params
        ),
    }


def get_gene_sequence(identifier, sequence_type="cdna"):
    """Retrieve genomic, cDNA, CDS or protein sequence."""
    allowed = {"genomic", "cdna", "cds", "protein"}

    if sequence_type not in allowed:
        raise ValueError("Unsupported sequence type.")

    endpoint = f"{BASE_URL}/sequence/id/{identifier.strip()}"
    params = {"type": sequence_type}

    sequence = request_text(
        endpoint,
        params=params,
        headers={"Content-Type": "text/plain"},
    )

    return {
        "identifier": identifier,
        "sequence_type": sequence_type,
        "sequence": sequence.strip(),
        "provenance": provenance(
            "Ensembl Plants", endpoint, params
        ),
    }


def get_cross_references(identifier):
    """Retrieve cross-references for an Ensembl identifier."""
    data, endpoint = _get(
        f"/xrefs/id/{identifier.strip()}",
        {"all_levels": 1},
    )

    return {
        "cross_references": data,
        "provenance": provenance(
            "Ensembl Plants",
            endpoint,
            {"all_levels": 1},
        ),
    }
