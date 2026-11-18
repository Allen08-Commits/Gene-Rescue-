
"""UniProt REST API integration."""

from urllib.parse import quote

from integrations import (
    request_json,
    request_text,
    provenance,
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
    """Search UniProtKB and return normalized protein records."""
    if not str(query).strip():
        raise ValueError("Enter a protein or gene search query.")

    page_size = size if size is not None else limit
    page_size = max(1, min(int(page_size), 100))

    search_query = f"({query})"

    if organism_id:
        search_query += f" AND (organism_id:{organism_id})"

    if reviewed_only:
        search_query += " AND (reviewed:true)"

    requested_fields = fields or [
        "accession",
        "id",
        "protein_name",
        "organism_name",
        "organism_id",
        "length",
        "reviewed",
    ]

    data = request_json(
        f"{BASE_URL}/uniprotkb/search",
        params={
            "query": search_query,
            "format": "json",
            "size": page_size,
            "fields": ",".join(requested_fields),
        },
    )

    results = []

    for record in data.get("results", []):
        organism = record.get("organism", {})
        protein_description = record.get(
            "proteinDescription", {}
        )

        recommended = protein_description.get(
            "recommendedName", {}
        )

        protein_name = (
            recommended.get("fullName", {}).get("value", "")
        )

        if not protein_name:
            submission = protein_description.get(
                "submissionNames", []
            )
            if submission:
                protein_name = (
                    submission[0].get("fullName", {}).get("value", "")
                )

        accession = record.get("primaryAccession", "")

        results.append({
            "accession": accession,
            "id": record.get("uniProtkbId", ""),
            "protein_name": protein_name,
            "organism": organism.get("scientificName", ""),
            "taxonomy_id": organism.get("taxonId"),
            "reviewed": record.get("entryType", "").lower().startswith(
                "reviewed"
            ),
            "sequence_length": record.get(
                "sequence", {}
            ).get("length"),
            "source_url": (
                f"https://www.uniprot.org/uniprotkb/{accession}/entry"
                if accession else ""
            ),
            "raw_record": record,
        })

    return results


def get_protein_entry(accession):
    """Retrieve a complete UniProtKB JSON entry."""
    endpoint = (
        f"{BASE_URL}/uniprotkb/"
        f"{quote(str(accession), safe='')}"
    )

    record = request_json(
        endpoint,
        params={"format": "json"},
    )

    return {
        "accession": accession,
        "record": record,
        "provenance": provenance(
            "UniProtKB",
            endpoint,
            accession,
        ),
    }


def get_protein_fasta(accession):
    """Retrieve a protein sequence in FASTA format."""
    endpoint = (
        f"{BASE_URL}/uniprotkb/"
        f"{quote(str(accession), safe='')}.fasta"
    )

    fasta = request_text(endpoint)

    return {
        "accession": accession,
        "fasta": fasta,
        "provenance": provenance(
            "UniProtKB",
            endpoint,
            accession,
        ),
    }
