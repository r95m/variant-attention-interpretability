#!/bin/bash

# Directory containing hg38
REF_DIR="/Users/rm1406/Desktop/variant-attention-interpretability/data/raw/genome"

FASTA="$REF_DIR/hg38.fa.gz"

# Sanity check
if [ ! -f "$FASTA" ]; then
  echo "ERROR: $FASTA not found"
  exit 1
fi

# Create FASTA index (.fai)
samtools faidx "$FASTA"

echo "Indexing complete:"
echo "$FASTA.fai"
