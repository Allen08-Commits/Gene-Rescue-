from integrations import ncbi
from integrations import uniprot
from integrations import ensembl_plants
from integrations import interpro
from integrations import pubmed
from integrations import gramene


def test_ncbi_functions_exist():
    assert callable(ncbi.search_gene)
    assert callable(ncbi.search_nucleotide)
    assert callable(ncbi.search_protein)


def test_uniprot_functions_exist():
    assert callable(uniprot.search_proteins)
    assert callable(uniprot.get_protein_entry)


def test_ensembl_functions_exist():
    assert callable(ensembl_plants.search_plant_genes)
    assert callable(ensembl_plants.lookup_gene)


def test_interpro_functions_exist():
    assert callable(interpro.search_protein_accession)


def test_pubmed_functions_exist():
    assert callable(pubmed.search_literature)


def test_gramene_functions_exist():
    assert callable(gramene.resource_links)