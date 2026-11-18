
"""UniProt integration for GeneRescue AI."""

from urllib.parse import quote

from integrations import (
    request_json,
    request_text,
    provenance,
    ExternalDatabaseError,
)

BASE_URL = "https://rest.uniprot.org"


def search_proteins(
    query,
    organism_id=None,
    reviewed_only=False,
    limit=10,
    size=None,
    fields=None,
):
    """Search UniProtKB and return a list of protein records."""

    if not query or not query.strip():
        raise ValueError("Enter a protein search query.")

    if size is not None:
        limit = size

    if not 1 <= int(limit) <= 500:
        raise ValueError("Limit must be between 1 and 500.")

    search_query = query.strip()

    if organism_id is not None:
        search_query += f" AND organism_id:{int(organism_id)}"

    if reviewed_only:
        search_query += " AND reviewed:true"

    endpoint = f"{BASE_URL}/uniprotkb/search"

    params = {
        "query": search_query,
        "format": "json",
        "size": int(limit),
    }

    if fields:
        params["fields"] = ",".join(fields)

    data = request_json(endpoint, params=params)

    records = []

    for item in data.get("results", []):
        accession = item.get("primaryAccession", "")

        protein_description = item.get(
            "proteinDescription", {}
        )

        recommended = protein_description.get(
            "recommendedName", {}
        )

        protein_name = recommended.get(
            "fullName", {}
        ).get("value", "")

        organism = item.get("organism", {})

        records.append({
            "accession": accession,
            "id": item.get("uniProtkbId", ""),
            "protein_name": protein_name,
            "organism": organism.get("scientificName", ""),
            "taxonomy_id": organism.get("taxonId"),
            "reviewed": item.get("entryType", ""),
            "sequence_length": item.get(
                "sequence", {}
            ).get("length"),
            "source_url": (
                f"https://www.uniprot.org/uniprotkb/{accession}"
                if accession else ""
            ),
            "raw_record": item,
        })

    return records


def get_protein_entry(accession):
    """Retrieve a complete UniProt protein entry."""

    if not accession or not accession.strip():
        raise ValueError("UniProt accession is required.")

    safe_id = quote(accession.strip(), safe="")
    endpoint = f"{BASE_URL}/uniprotkb/{safe_id}"

    params = {"format": "json"}

    data = request_json(endpoint, params=params)

    return {
        "accession": accession,
        "record": data,
        "provenance": provenance(
            "UniProtKB",
            endpoint,
            params,
        ),
    }


def get_protein_fasta(accession):
    """Retrieve a protein sequence in FASTA format."""

    if not accession or not accession.strip():
        raise ValueError("UniProt accession is required.")

    safe_id = quote(accession.strip(), safe="")
    endpoint = f"{BASE_URL}/uniprotkb/{safe_id}.fasta"

    fasta = request_text(endpoint)

    if not fasta.strip().startswith(">"):
        raise ExternalDatabaseError(
            "UniProt did not return valid FASTA data."
        )

    return {
        "accession": accession,
        "fasta": fasta.strip(),
        "provenance": provenance(
            "UniProtKB",
            endpoint,
            {},
        ),
    }
