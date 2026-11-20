"""
ETL Pipeline for NHTSA Data Ingestion and Ground Truth Labeling.
Maintained by Mahdy (with Ghadeer & Aya).
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
    'CONEQUENCE_DEFECT','CORRECTIVE_ACTION', 'NOTES', 'RCL_CMPT_ID',
    'EXTRA_25', 'EXTRA_26', 'EXTRA_27','EXTRA_28', 'EXTRA_29'
]


COMPLAINT_COLUMNS = [
    'CMPLID', 'ODINO', 'MFR_NAME', 'MAKETXT', 'MODELTXT',
    'YEARTXT', 'CRASH', 'FAILDATE', 'FIRE', 'INJURED',
    'DEATHS', 'COMPDESC', 'CITY', 'STATE', 'VIN',
    'DATEA', 'LDATE', 'MILES', 'OCCURENCES', 'CDESCR',
    'CMPL_TYPE', 'POLICE_RPT_YN', 'PURCH_DT',
    'ORIG_OWNER_YN', 'ANTI_BRAKES_YN', 'CRUISE_CONT_YN',
    'NUM_CYLS', 'DRIVE_TRAIN', 'FUEL_SYS', 'FUEL_TYPE',
    'TRANS_TYPE', 'VEH_SPEED', 'DOT', 'TIRE_SIZE',
    'LOC_OF_TIRE', 'TIRE_FAIL_TYPE', 'ORIG_EQUIP_YN',
    'MANUF_DT', 'SEAT_TYPE', 'RESTRAINT_TYPE',
    'DEALER_NAME', 'DEALER_TEL', 'DEALER_CITY',
    'DEALER_STATE', 'DEALER_ZIP', 'PROD_TYPE',
    'REPAIRED_YN', 'MEDICAL_ATTN', 'VEHICLES_TOWED_YN',
    'STATE_OF_INCIDENT', 'VEHICLE_OPERATOR'
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
        dtype={'YEARTXT': str},
        low_memory=False
    )
    # Standardize join keys
    df['MAKE_CLEAN'] = df['MAKETXT'].astype(str).str.strip().str.upper()
    df['MODEL_CLEAN'] = df['MODELTXT'].astype(str).str.strip().str.upper()
    df['YEAR_CLEAN'] = pd.to_numeric(df['YEARTXT'], errors='coerce')
    df['COMP_CLEAN'] = df['COMPNAME'].astype(str).str.strip().str.upper()
    df['COMP_MAIN'] = df['COMP_CLEAN'].str.split(':').str[0].str.strip()
    df['RECALL_DATE'] = pd.to_datetime(df['RCDATE'].astype(str), format='%Y%m%d', errors='coerce')
    return df

def standardize_complaints(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize complaint fields for matching and labeling."""
    df = df.copy()

    df["MAKE_CLEAN"] = df["MAKETXT"].astype(str).str.strip().str.upper()
    df["MODEL_CLEAN"] = df["MODELTXT"].astype(str).str.strip().str.upper()
    df["YEAR_CLEAN"] = pd.to_numeric(df["YEARTXT"], errors="coerce")

    df["COMP_CLEAN"] = df["COMPDESC"].astype(str).str.strip().str.upper()
    df["COMP_MAIN"] = df["COMP_CLEAN"].str.split(":").str[0].str.strip()

    df["COMPLAINT_DATE"] = pd.to_datetime(
        df["DATEA"].astype(str),
        format="%Y%m%d",
        errors="coerce",
    )

    return df


def filter_eligible_complaints(df: pd.DataFrame) -> pd.DataFrame:
    """Keep complaints eligible for 365-day recall labeling."""

    df = df.copy()

    # Restrict complaints to the validated observation period
    start_date = pd.Timestamp("2010-01-01")
    end_date = pd.Timestamp("2025-11-12")

    date_mask = df["COMPLAINT_DATE"].between(
        start_date, end_date
    )

    # Require valid vehicle matching information
    keys = ["MAKE_CLEAN", "MODEL_CLEAN", "YEAR_CLEAN", "COMP_MAIN"]

    valid_keys = df[keys].notna().all(axis=1)

    for col in ["MAKE_CLEAN", "MODEL_CLEAN", "COMP_MAIN"]:
        valid_keys &= ~df[col].isin(["", "NAN", "NONE", "NULL"])

    filtered = df.loc[date_mask & valid_keys].copy()

    print(f"Eligible complaints: {len(filtered):,}")
    print(f"Excluded complaints: {len(df) - len(filtered):,}")

    return filtered


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
    dtype={
        'YEARTXT': str,
        'DATEA': str,
        'LDATE': str
    },
    low_memory=False
    )
    df['MAKE_CLEAN'] = df['MAKETXT'].astype(str).str.strip().str.upper()
    df['MODEL_CLEAN'] = df['MODELTXT'].astype(str).str.strip().str.upper()
    df['YEAR_CLEAN'] = pd.to_numeric(df['YEARTXT'], errors='coerce')
    df['COMP_CLEAN'] = df['COMPDESC'].astype(str).str.strip().str.upper()
    df['COMP_MAIN'] = df['COMP_CLEAN'].str.split(':').str[0].str.strip()
    df['COMPLAINT_DATE'] = pd.to_datetime(df['DATEA'].astype(str), format='%Y%m%d', errors='coerce')
    return df



def build_labeled_dataset(
    df_cmpl: pd.DataFrame,
    df_rcl: pd.DataFrame,
    batch_size: int = 10_000,
) -> pd.DataFrame:
    """
    Label complaints 1 when a matching recall occurs 1-365 days later.
    Keep one row per complaint and process complaints in batches.
    """
    print("Matching complaints with official recalls...")

    keys = ["MAKE_CLEAN", "MODEL_CLEAN", "YEAR_CLEAN", "COMP_MAIN"]
    recall_cols = keys + ["RECALL_DATE", "CAMPNO", "DESC_DEFECT"]

    recalls = df_rcl[recall_cols].dropna(
        subset=keys + ["RECALL_DATE"]
    ).copy()

    # Keep recalls sorted so the earliest valid future recall wins.
    recall_groups = {
        key: group.sort_values("RECALL_DATE")
        for key, group in recalls.groupby(keys, sort=False)
    }

    results = []

    for start in range(0, len(df_cmpl), batch_size):
        batch = df_cmpl.iloc[start:start + batch_size].copy()

        batch["RECALL_DATE"] = pd.NaT
        batch["CAMPNO"] = None
        batch["DESC_DEFECT"] = None
        batch["DAYS_TO_RECALL"] = float("nan")
        batch["TARGET_RECALL_12M"] = 0

        for idx, complaint in batch.iterrows():
            key = tuple(complaint[col] for col in keys)

            if any(pd.isna(value) for value in key):
                continue

            matches = recall_groups.get(key)
            if matches is None:
                continue

            complaint_date = complaint["COMPLAINT_DATE"]
            if pd.isna(complaint_date):
                continue

            future = matches.loc[
                (matches["RECALL_DATE"] > complaint_date)
                & (
                    matches["RECALL_DATE"]
                    <= complaint_date + pd.Timedelta(days=365)
                )
            ]

            if not future.empty:
                recall = future.iloc[0]
                days = (recall["RECALL_DATE"] - complaint_date).days

                batch.at[idx, "RECALL_DATE"] = recall["RECALL_DATE"]
                batch.at[idx, "CAMPNO"] = recall["CAMPNO"]
                batch.at[idx, "DESC_DEFECT"] = recall["DESC_DEFECT"]
                batch.at[idx, "DAYS_TO_RECALL"] = days
                batch.at[idx, "TARGET_RECALL_12M"] = 1

        results.append(batch)
        print(f"Processed {min(start + batch_size, len(df_cmpl)):,} / {len(df_cmpl):,}")

    labeled = pd.concat(results, ignore_index=True)

    print(f"Total labeled records: {len(labeled):,}")
    print(f"Positive recall rate: {labeled['TARGET_RECALL_12M'].mean():.4f}")

    return labeled



def main():
    parser = argparse.ArgumentParser(description="RecallRadar ETL Starter")
    parser.add_argument("--sample", action="store_true", help="Run in quick sample mode (first 25k rows)")
    parser.add_argument("--download", action="store_true", help="Download raw files from NHTSA")
    args = parser.parse_args()

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_dir = (
    PROCESSED_DATA_DIR / "sample_test"
    if args.sample
    else PROCESSED_DATA_DIR
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    recalls_zip = RAW_DATA_DIR / "FLAT_RCL_POST_2010.zip"
    complaints_zip = RAW_DATA_DIR / "FLAT_CMPL.zip"

    if args.download:
        download_file(RECALLS_URL, recalls_zip)
        download_file(COMPLAINTS_URL, complaints_zip)

    if not recalls_zip.exists() or not complaints_zip.exists():
        print(f"\n[!] Raw data files not found in {RAW_DATA_DIR}")
        print("Please download them manually or run with: python src/etl.py --download")
        return

    # Always load all recalls for accurate ground truth
    df_rcl = load_recalls_sample(recalls_zip, nrows=None)

    # Load complaints, then select eligible sample records
    df_cmpl = load_complaints_sample(complaints_zip, nrows=None)

    # Keep only complaints eligible for 12-month labeling
    df_cmpl = filter_eligible_complaints(df_cmpl)
    if args.sample:
        df_cmpl = df_cmpl.head(25000).copy()
        print(f"Selected {len(df_cmpl):,} eligible complaints for testing.")
    if df_cmpl.empty:
        print("No eligible complaints found in this sample.")
        print("Try a different sample or run the full dataset.")
        return

    # Match eligible complaints with official recalls
    df_labeled = build_labeled_dataset(df_cmpl, df_rcl)
    
    output_file = output_dir / "labeled_complaints_sample.csv"
    df_labeled.to_csv(output_file, index=False)
    print(f"Saved labeled dataset to {output_file}")

    # Export the required Parquet files
    # Export clean complaints without future recall information
    future_columns = [
        "TARGET_RECALL_12M",
        "RECALL_DATE",
        "CAMPNO",
        "DESC_DEFECT",
        "DAYS_TO_RECALL",
    ]

    clean_df = df_labeled.drop(
        columns=future_columns,
        errors="ignore"
    )

    clean_output = output_dir / "clean_complaints.parquet"
    clean_df.to_parquet(clean_output, index=False)

    # Export ground truth labels
    labels_df = df_labeled[["CMPLID", "TARGET_RECALL_12M"]].copy()

    labels_df = labels_df.rename(
        columns={"TARGET_RECALL_12M": "recall_within_12m"}
    )

    labels_df["recall_within_12m"] = (
        labels_df["recall_within_12m"].astype("int8")
    )

    labels_output = output_dir / "labels.parquet"
    labels_df.to_parquet(labels_output, index=False)

    print(f"Saved clean complaints: {clean_output}")
    print(f"Saved labels: {labels_output}")
    print(f"Total records: {len(labels_df):,}")
    print(f"Positive labels: {labels_df['recall_within_12m'].sum():,}")
if __name__ == "__main__":
    main()
