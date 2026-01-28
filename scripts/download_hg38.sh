#!/bin/bash

# Directory inside the repo where hg38 should live
REF_DIR="/Users/rm1406/Desktop/variant-attention-interpretability/data/raw/genome"

# Create directory if it doesn't exist
mkdir -p "$REF_DIR"

# Download hg38 reference genome
wget -O "$REF_DIR/hg38.fa.gz" \
  https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz

echo "hg38 download complete:"
echo "$REF_DIR/hg38.fa.gz"
