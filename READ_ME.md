# Variant Attention Interpretability

This repository contains a technical analysis of how a pretrained genomic foundation model responds to single-nucleotide variants (SNVs), with a focus on **model interpretability rather than predictive performance**. The goal of the project is to characterize how sequence perturbations redistribute model attention, assess the spatial structure of these perturbations, and test whether variant-token representations causally drive attention changes using activation patching.

All analyses were conducted as part of a technical evaluation and are designed to be transparent, reproducible, and easy to follow.

---

## Project Overview

We analyze attention patterns from a pretrained nucleotide transformer model when presented with reference and alternate allele sequences derived from ClinVar variants. Specifically, we:

- Quantify attention perturbations induced by SNVs as a function of distance from the variant
- Assess locality and centrality of variant-associated attention changes
- Compare patterns across functional and clinical variant classes
- Use **activation patching** to test whether variant-token representations causally drive attention redistribution
- Visualize aggregate and per-variant attention effects

---

## Repository Structure

variant-attention-interpretability/
├── data/
│ ├── raw/
│ │ ├── clinvar/ # Raw ClinVar VCF files
│ │ └── genome/ # Reference genome (hg38)
│ ├── processed/
│ │ ├── clinvar_clean/ # Filtered and balanced ClinVar tables
│ │ ├── model_input/ # Variant-centered sequence inputs
│ │ └── model_output/ # Attention perturbation outputs
│
├── notebooks/
│ ├── part_001_import_clinvar_n_clean.ipynb
│ ├── part_002_clinvar_variant_sequence_hg38.ipynb
│ ├── part_003_run_model_n_patching.ipynb
│ └── part_004_model_analysis_n_plots.ipynb
│
├── results/
│ ├── figures/ # Main and supplemental figures
│ └── tables/ # Tabular model outputs
│
├── report/
│ └── McNeil_Reid_Genomic_Interpretability_Jan_2026.pdf
│
├── environment.yml # Conda environment specification
└── README.md


---

## Data Sources

- **ClinVar**: Single-nucleotide variants annotated with clinical significance and functional class
- **Reference Genome**: hg38 (FASTA + index)

Raw data are stored under `data/raw/`. All downstream datasets used for modeling and analysis are stored under `data/processed/`.

---

## Analysis Workflow

The analysis is organized as a sequence of notebooks:

1. **ClinVar ingestion and cleaning**  
   `part_001_import_clinvar_n_clean.ipynb`  
   - Load ClinVar VCF
   - Filter to SNVs
   - Balance variants across clinical classes
   - Save cleaned tables

2. **Sequence extraction**  
   `part_002_clinvar_variant_sequence_hg38.ipynb`  
   - Extract variant-centered DNA sequences from hg38
   - Generate reference and alternate allele sequences
   - Save model input CSVs

3. **Model inference and activation patching**  
   `part_003_run_model_n_patching.ipynb`  
   - Run pretrained nucleotide transformer
   - Extract attention representations
   - Perform activation patching at the variant token
   - Save attention perturbation outputs

4. **Analysis and visualization**  
   `part_004_model_analysis_n_plots.ipynb`  
   - Quantify locality and centrality of attention perturbations
   - Stratify results by functional and clinical class
   - Generate all figures included in the report

---

## Outputs

Key outputs include:

- **Attention perturbation tables**  
  `data/processed/model_output/variant_attention_deltas_100bp.pkl`

- **Figures**  
  Stored under `results/figures/`, including:
  - Locality of attention perturbation
  - Variant token centrality
  - Distance-decay profiles
  - Activation patching rescue effects
  - Supplemental variant distribution plots

---

## Environment

All dependencies are specified in `environment.yml`.  
To recreate the environment:

```bash
conda env create -f environment.yml
conda activate genomic-fm
pip install -r requirements.txt
jupyter lab
```

