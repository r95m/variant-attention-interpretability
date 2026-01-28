#!/bin/bash

# Exit immediately if something fails
set -e

# GitHub repo URL
REPO_URL="https://github.com/bowang-lab/genomic-FM.git"

# Clone into current directory
git clone "$REPO_URL"

echo "Repository cloned successfully:"
echo "genomic-FM/"
