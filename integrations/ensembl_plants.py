
"""Ensembl Plants REST API integration."""

from integrations import (
    ExternalDatabaseError,
    provenance,
    request_json,
    request_text,
)

BASE_URL = "https://rest.ensembl.org"


def _plant_get(path: str, params: dict | None = None):
    url = BASE_URL + path
    headers = {"Accept": "application/json"}
    data = request_json(url, params=params, headers=headers)
    return data, url


def lookup_gene(identifier: str, expand: bool = True) -> dict:
    """Retrieve an Ensembl gene or transcript record by stable ID."""
    if not identifier.strip():
        raise ValueError("Enter an Ensembl stable identifier.")

    params = {"expand": 1 if expand else 0}
    data, url = _plant_get(
        f"/lookup/id/{identifier.strip()}",
        params=params,
    )

    return {
        "identifier": identifier,
        "record": data,
        "provenance": provenance("Ensembl REST", url, params),
    }


def get_gene_sequence(
    identifier: str,
    sequence_type: str = "genomic",
) -> dict:
    """Retrieve a sequence by Ensembl stable identifier."""
    allowed = {"genomic", "cdna", "cds", "protein"}
    if sequence_type not in allowed:
        raise ValueError(
            "Sequence type must be genomic, cdna, cds or protein."
        )

    url = f"{BASE_URL}/sequence/id/{identifier.strip()}"
    params = {"type": sequence_type}

    sequence = request_text(
        url,
        params=params,
        headers={"Content-Type": "application/json"},
    )

    return {
        "identifier": identifier,
        "sequence_type": sequence_type,
        "sequence": sequence.strip(),
        "provenance": provenance("Ensembl REST", url, params),
    }


def get_cross_references(identifier: str) -> dict:
    """Retrieve external database cross-references for an Ensembl ID."""
    data, url = _plant_get(
        f"/xrefs/id/{identifier.strip()}",
        params={"all_levels": 1},
    )

    return {
        "identifier": identifier,
        "cross_references": data,
        "provenance": provenance(
            "Ensembl REST",
            url,
            {"all_levels": 1},
        ),
    }


def search_gene_symbol(species: str, symbol: str) -> dict:
    """Search Ensembl cross-references by species and gene symbol."""
    if not species.strip() or not symbol.strip():
        raise ValueError("Species and gene symbol are required.")

    params = {"external_db": ""}
    data, url = _plant_get(
        f"/xrefs/symbol/{species.strip()}/{symbol.strip()}",
        params=params,
    )

    return {
        "species": species,
        "symbol": symbol,
        "matches": data,
        "provenance": provenance("Ensembl REST", url, params),
    }
