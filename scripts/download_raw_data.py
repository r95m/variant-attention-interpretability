#!/usr/bin/env python3
"""
Download raw datasets (ClinVar VCF + hg38 reference genome) into this repo.

Outputs:
  data/raw/clinvar/clinvar_*.vcf.gz (+ .tbi)
  data/raw/genome/hg38.fa (+ .fai)

Usage:
  python scripts/download_raw_data.py --all
  python scripts/download_raw_data.py --clinvar
  python scripts/download_raw_data.py --genome

Notes:
- This script does NOT commit large files to git.
- Requires: python, pip/conda env with pysam (recommended) OR samtools on PATH.
"""

from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"
CLINVAR_DIR = RAW_DIR / "clinvar"
GENOME_DIR = RAW_DIR / "genome"

# --- Customize if you want a specific genome URL you used ---
# UCSC hg38 reference (2bit) is common, but you used a FASTA already.
# If you used a different hg38.fa URL, replace HG38_FASTA_URL with yours.
HG38_FASTA_URL = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz"
HG38_FASTA_GZ = GENOME_DIR / "hg38.fa.gz"
HG38_FASTA = GENOME_DIR / "hg38.fa"

def run(cmd: list[str], check: bool = True) -> None:
    print(">>", " ".join(cmd))
    subprocess.run(cmd, check=check)

def ensure_dirs() -> None:
    CLINVAR_DIR.mkdir(parents=True, exist_ok=True)
    GENOME_DIR.mkdir(parents=True, exist_ok=True)

def have_exe(name: str) -> bool:
    return shutil.which(name) is not None

def download_file(url: str, outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)

    if outpath.exists() and outpath.stat().st_size > 0:
        print(f"[skip] exists: {outpath}")
        return

    if have_exe("curl"):
        run(["curl", "-L", url, "-o", str(outpath)])
    elif have_exe("wget"):
        run(["wget", "-O", str(outpath), url])
    else:
        raise RuntimeError("Need curl or wget installed to download files.")

def gunzip_to(src_gz: Path, dst: Path) -> None:
    if dst.exists() and dst.stat().st_size > 0:
        print(f"[skip] exists: {dst}")
        return
    if not have_exe("gunzip"):
        raise RuntimeError("gunzip not found. Install gzip utilities or use macOS default gunzip.")
    # -c writes to stdout
    run(["gunzip", "-c", str(src_gz)], check=True)
    # We need to redirect output to file; use shell=False workaround with Python:
    with open(dst, "wb") as f_out:
        p = subprocess.Popen(["gunzip", "-c", str(src_gz)], stdout=f_out)
        rc = p.wait()
        if rc != 0:
            raise RuntimeError(f"gunzip failed with exit code {rc}")

def ensure_fai(fasta_path: Path) -> None:
    fai_path = Path(str(fasta_path) + ".fai")
    if fai_path.exists() and fai_path.stat().st_size > 0:
        print(f"[ok] found index: {fai_path.name}")
        return

    # Prefer pysam if installed
    try:
        import pysam  # type: ignore
        print("[index] building .fai with pysam")
        pysam.faidx(str(fasta_path))
        return
    except Exception:
        pass

    # Else fall back to samtools
    if have_exe("samtools"):
        print("[index] building .fai with samtools")
        run(["samtools", "faidx", str(fasta_path)])
        return

    raise RuntimeError(
        "Could not create hg38.fa.fai. Install pysam (pip install pysam) or samtools."
    )

def download_genome() -> None:
    """
    Downloads hg38.fa.gz and extracts to hg38.fa, then ensures hg38.fa.fai exists.
    """
    print("\n=== Downloading hg38 reference ===")
    ensure_dirs()
    download_file(HG38_FASTA_URL, HG38_FASTA_GZ)
    gunzip_to(HG38_FASTA_GZ, HG38_FASTA)
    ensure_fai(HG38_FASTA)
    print(f"[done] genome at: {HG38_FASTA}")

def run_genomic_fm_clinvar() -> None:
    """
    Uses the external genomic-FM repo downloader if it exists locally.
    You said you used: data/genomic-FM/download_data.py
    We'll call that if present.

    Output files should land in your repo's data/raw/clinvar directory.
    """
    print("\n=== Downloading ClinVar via genomic-FM downloader ===")
    ensure_dirs()

    genomic_fm_dir = REPO_ROOT / "data" / "genomic-FM"
    dl_script = genomic_fm_dir / "download_data.py"

    if not dl_script.exists():
        raise RuntimeError(
            "Could not find data/genomic-FM/download_data.py.\n"
            "Options:\n"
            "  1) Vendor the genomic-FM downloader into this repo under data/genomic-FM/\n"
            "  2) Or replace this function to download ClinVar directly from NCBI FTP.\n"
        )

    # Try to run their downloader. We don't know their exact CLI args,
    # so we provide a few common patterns. You can adjust once you confirm the script interface.
    #
    # Best practice: make it write into YOUR repo path (CLINVAR_DIR).
    #
    # If their script doesn't support output dir, you can run it then move outputs.
    possible_cmds = [
        [sys.executable, str(dl_script), "--clinvar", "--outdir", str(CLINVAR_DIR)],
        [sys.executable, str(dl_script), "--clinvar", "--output", str(CLINVAR_DIR)],
        [sys.executable, str(dl_script), "--clinvar"],
    ]

    last_err = None
    for cmd in possible_cmds:
        try:
            run(cmd, check=True)
            last_err = None
            break
        except subprocess.CalledProcessError as e:
            last_err = e

    if last_err is not None:
        raise RuntimeError(
            "Failed to run genomic-FM ClinVar downloader.\n"
            "Open data/genomic-FM/download_data.py and confirm its CLI arguments, then update\n"
            "the 'possible_cmds' list in scripts/download_raw_data.py.\n"
            f"Last error: {last_err}"
        )

    # If it downloaded into genomic-FM locations, try to copy matching clinvar files into CLINVAR_DIR
    # (safe, no harm if files already exist).
    for p in genomic_fm_dir.rglob("clinvar*.vcf.gz"):
        target = CLINVAR_DIR / p.name
        if not target.exists():
            shutil.copy2(p, target)
            print(f"[copy] {p} -> {target}")

    for p in genomic_fm_dir.rglob("clinvar*.tbi"):
        target = CLINVAR_DIR / p.name
        if not target.exists():
            shutil.copy2(p, target)
            print(f"[copy] {p} -> {target}")

    print(f"[done] clinvar directory: {CLINVAR_DIR}")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Download genome + ClinVar")
    parser.add_argument("--genome", action="store_true", help="Download hg38")
    parser.add_argument("--clinvar", action="store_true", help="Download ClinVar")
    args = parser.parse_args()

    if not (args.all or args.genome or args.clinvar):
        parser.error("Choose one: --all, --genome, or --clinvar")

    if args.all or args.genome:
        download_genome()

    if args.all or args.clinvar:
        run_genomic_fm_clinvar()

if __name__ == "__main__":
    main()
