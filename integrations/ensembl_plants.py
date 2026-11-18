
"""Ensembl Plants REST API integration."""

from urllib.parse import quote

from integrations import request_json, request_text, provenance


BASE_URL = "https://rest.ensembl.org"


def search_plant_genes(query, species="oryza_sativa"):
    """Search Ensembl Plants gene symbols and cross-references."""
    if not str(query).strip():
        raise ValueError("Enter a gene symbol or identifier.")

    endpoint = (
        f"{BASE_URL}/xrefs/symbol/"
        f"{quote(species, safe='')}/"
        f"{quote(str(query), safe='')}"
    )

    records = request_json(
        endpoint,
        headers={"Content-Type": "application/json"},
    )

    results = []

    for record in records:
        results.append({
            "id": record.get("id", ""),
            "type": record.get("type", ""),
            "display_id": record.get("display_id", ""),
            "description": record.get("description", ""),
            "species": species,
            "source_url": endpoint,
        })

    return results


def lookup_gene(identifier, expand=False):
    """Retrieve an Ensembl gene record."""
    endpoint = (
        f"{BASE_URL}/lookup/id/"
        f"{quote(str(identifier), safe='')}"
    )

    data = request_json(
        endpoint,
        params={"expand": int(bool(expand))},
        headers={"Content-Type": "application/json"},
    )

    data["_provenance"] = provenance(
        "Ensembl Plants",
        endpoint,
        identifier,
    )

    return data


def get_gene_sequence(identifier, sequence_type="genomic"):
    """Retrieve genomic, cDNA or CDS sequence."""
    allowed = {"genomic", "cdna", "cds", "protein"}

    if sequence_type not in allowed:
        raise ValueError(
            f"Sequence type must be one of: {', '.join(sorted(allowed))}"
        )

    endpoint = (
        f"{BASE_URL}/sequence/id/"
        f"{quote(str(identifier), safe='')}"
    )

    sequence = request_text(
        endpoint,
        params={"type": sequence_type},
        headers={"Content-Type": "text/plain"},
    )

    return {
        "identifier": str(identifier),
        "sequence_type": sequence_type,
        "sequence": sequence.strip(),
        "source_url": endpoint,
    }


def get_cross_references(identifier):
    """Retrieve cross-references associated with an Ensembl identifier."""
    endpoint = (
        f"{BASE_URL}/xrefs/id/"
        f"{quote(str(identifier), safe='')}"
    )

    return request_json(
        endpoint,
        headers={"Content-Type": "application/json"},
    )
