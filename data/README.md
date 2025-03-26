# Data Directory

This directory contains all the data used in the project.

## Directory Structure

- `raw/`: Original, immutable data
- `processed/`: Cleaned and processed data, derived from raw data
- `external/`: Data from external sources, used for reference

## Data Dictionary

Add information about your datasets here:

| Dataset | Description | Source | Date Obtained |
|---------|-------------|--------|---------------|
| example.csv | Example dataset | [Source URL] | YYYY-MM-DD |

### GSM321647.mev 
- mev file selected at random from https://github.com/tracelail/comparative-transcriptomics-of-resilient-vs-susceptible-coral-species.git
- to me subset into `test-mev-file.mev` for pipeline creation
- source: https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-GEOD-15262?query=thermal%20stress%20coral%20rna%20sequence
- Date obtained: 2025-02-18
- accession: `E-GEOD-15262`

### Array design matrix
- Found array design matrix A-GEOD-7317. https://www.ebi.ac.uk/biostudies/arrayexpress/arrays/A-GEOD-7317
- This was mentioned in the E-GEOD-15262.sdrf.txt

### reference genome
- Could not find Montastraea faveolata genome but found Orbicella faveolata.
    - Montastraea faveolata is a homotypic synonym for Orbicella faveolata.
- genome: https://www.ncbi.nlm.nih.gov/nuccore/NC_007226.1/
- Accession: NC_007226
- Version: NC_007226.1

## Notes

