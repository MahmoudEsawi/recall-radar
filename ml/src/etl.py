"""
ETL Pipeline for NHTSA Data Ingestion and Ground Truth Labeling.
Maintained by Ghadeer & Aya.
"""

import os
import sys
import argparse
import urllib.request
import zipfile
import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# NHTSA URLs
RECALLS_URL = "https://static.nhtsa.gov/odi/ffdd/rcl/FLAT_RCL_POST_2010.zip"
COMPLAINTS_URL = "https://static.nhtsa.gov/odi/ffdd/cmpl/FLAT_CMPL.zip"

RECALL_COLUMNS = [
    'RECORD_ID', 'CAMPNO', 'MAKETXT', 'MODELTXT', 'YEARTXT', 
    'MFGCAMPNO', 'COMPNAME', 'MFGNAME', 'BGMAN', 'ENDMAN', 
    'RCLTYPECD', 'POTAFF', 'ODATE', 'INFLUENCED_BY', 'MFGTXT', 
    'RCDATE', 'DATEA', 'RPNO', 'FMVSS', 'DESC_DEFECT', 
    'CONEQUENCE_DEFECT', 'CORRECTIVE_ACTION', 'NOTES', 'RCL_CMPT_ID'
]

COMPLAINT_COLUMNS = [
    'CMPLID', 'ODINO', 'MFR_NAME', 'MAKETXT', 'MODELTXT', 'YEARTXT',
    'CRASH', 'FAILDATE', 'FIRE', 'INJURED', 'DEATHS', 'COMPNAME',
    'CITY', 'STATE', 'VIN', 'DATEA', 'LDATE', 'MILES', 'OCCURENCES',
    'CDESCR', 'CMPL_TYPE', 'POLICE_RPT_YN', 'ORIG_OWNER_YN', 'ANTI_BRAKES_YN',
    'CRUISE_CONT_YN', 'NUM_CYLS', 'DRIVE_TRAIN', 'FUEL_SYS', 'FUEL_TYPE',
    'TRANS_TYPE', 'VEH_SPEED', 'DOT', 'TIRE_SIZE', 'LOC_OF_TIRE', 'TIRE_FAIL_TYPE',
    'ORIG_EQUIP_YN', 'MANUFACTURE_DT', 'SEAT_TYPE', 'RESTRAINT_TYPE', 'DEALER_NAME',
    'DEALER_CITY', 'DEALER_STATE', 'DEALER_ZIP', 'PROD_TYPE', 'REPAIRED_YN',
    'MEDICAL_ATTN', 'VEHICLES_TOWED_YN'
]


def download_file(url: str, dest_path: Path):
    """Downloads a file if not already present."""
    if not dest_path.exists():
        print(f"Downloading {url} -> {dest_path}...")
        urllib.request.urlretrieve(url, dest_path)
        print("Download complete.")
    else:
        print(f"File already exists: {dest_path}")


def load_recalls_sample(zip_path: Path, nrows: int = 50000) -> pd.DataFrame:
    """Loads and standardizes official NHTSA recalls data."""
    print("Reading recalls...")
    df = pd.read_csv(
        zip_path,
        sep='\t',
        names=RECALL_COLUMNS,
        encoding='latin1',
        on_bad_lines='skip',
        nrows=nrows,
        dtype={'YEARTXT': str}
    )
    # Standardize join keys
    df['MAKE_CLEAN'] = df['MAKETXT'].astype(str).str.strip().str.upper()
    df['MODEL_CLEAN'] = df['MODELTXT'].astype(str).str.strip().str.upper()
    df['YEAR_CLEAN'] = pd.to_numeric(df['YEARTXT'], errors='coerce')
    df['COMP_CLEAN'] = df['COMPNAME'].astype(str).str.strip().str.upper()
    df['RECALL_DATE'] = pd.to_datetime(df['BGMAN'].astype(str), format='%Y%m%d', errors='coerce')
    return df


def load_complaints_sample(zip_path: Path, nrows: int = 50000) -> pd.DataFrame:
    """Loads and standardizes consumer complaints data."""
    print("Reading complaints...")
    df = pd.read_csv(
        zip_path,
        sep='\t',
        names=COMPLAINT_COLUMNS,
        encoding='latin1',
        on_bad_lines='skip',
        nrows=nrows,
        dtype={'YEARTXT': str}
    )
    df['MAKE_CLEAN'] = df['MAKETXT'].astype(str).str.strip().str.upper()
    df['MODEL_CLEAN'] = df['MODELTXT'].astype(str).str.strip().str.upper()
    df['YEAR_CLEAN'] = pd.to_numeric(df['YEARTXT'], errors='coerce')
    df['COMP_CLEAN'] = df['COMPNAME'].astype(str).str.strip().str.upper()
    df['COMPLAINT_DATE'] = pd.to_datetime(df['DATEA'].astype(str), format='%Y%m%d', errors='coerce')
    return df


def build_labeled_dataset(df_cmpl: pd.DataFrame, df_rcl: pd.DataFrame) -> pd.DataFrame:
    """
    Labels complaints: 1 if vehicle & component was officially recalled
    within 12 months after the complaint date; else 0.
    """
    print("Matching complaints with official recalls...")
    # Group recalls by vehicle unit
    recalls_indexed = df_rcl.dropna(subset=['MAKE_CLEAN', 'MODEL_CLEAN', 'YEAR_CLEAN', 'RECALL_DATE'])
    
    # Simple demonstration match on Make, Model, Year
    merged = pd.merge(
        df_cmpl,
        recalls_indexed[['MAKE_CLEAN', 'MODEL_CLEAN', 'YEAR_CLEAN', 'RECALL_DATE', 'CAMPNO', 'DESC_DEFECT']],
        on=['MAKE_CLEAN', 'MODEL_CLEAN', 'YEAR_CLEAN'],
        how='left'
    )
    
    # Calculate days between complaint date and official recall date
    merged['DAYS_TO_RECALL'] = (merged['RECALL_DATE'] - merged['COMPLAINT_DATE']).dt.days
    
    # Binary target: Recalled within 1 to 365 days after complaint
    merged['TARGET_RECALL_12M'] = (
        (merged['DAYS_TO_RECALL'] > 0) & (merged['DAYS_TO_RECALL'] <= 365)
    ).astype(int)
    
    print(f"Total labeled records: {len(merged)}")
    print(f"Positive recall rate: {merged['TARGET_RECALL_12M'].mean():.4f}")
    return merged


def main():
    parser = argparse.ArgumentParser(description="RecallRadar ETL Starter")
    parser.add_argument("--sample", action="store_true", help="Run in quick sample mode (first 25k rows)")
    parser.add_argument("--download", action="store_true", help="Download raw files from NHTSA")
    args = parser.parse_args()

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    recalls_zip = RAW_DATA_DIR / "FLAT_RCL_POST_2010.zip"
    complaints_zip = RAW_DATA_DIR / "FLAT_CMPL.zip"

    if args.download:
        download_file(RECALLS_URL, recalls_zip)
        download_file(COMPLAINTS_URL, complaints_zip)

    if not recalls_zip.exists() or not complaints_zip.exists():
        print(f"\n[!] Raw data files not found in {RAW_DATA_DIR}")
        print("Please download them manually or run with: python src/etl.py --download")
        return

    nrows = 25000 if args.sample else None
    df_rcl = load_recalls_sample(recalls_zip, nrows=nrows)
    df_cmpl = load_complaints_sample(complaints_zip, nrows=nrows)
    
    df_labeled = build_labeled_dataset(df_cmpl, df_rcl)
    
    output_file = PROCESSED_DATA_DIR / "labeled_complaints_sample.parquet"
    df_labeled.to_parquet(output_file, index=False)
    print(f"Saved processed sample dataset to {output_file}")


if __name__ == "__main__":
    main()
