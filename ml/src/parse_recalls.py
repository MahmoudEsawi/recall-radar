"""
Script to build a high-quality real NHTSA benchmark dataset
combining the official FLAT_RCL_POST_2010 recalls file and real complaints via NHTSA API.
"""

import json
import urllib.request
import urllib.parse
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

RECALL_COLS_29 = [
    'RECORD_ID', 'CAMPNO', 'MAKETXT', 'MODELTXT', 'YEARTXT', 
    'MFGCAMPNO', 'COMPNAME', 'MFGNAME', 'BGMAN', 'ENDMAN', 
    'RCLTYPECD', 'POTAFF', 'ODATE', 'INFLUENCED_BY', 'MFGTXT', 
    'RCDATE', 'DATEA', 'RPNO', 'FMVSS', 'DESC_DEFECT', 
    'CONEQUENCE_DEFECT', 'CORRECTIVE_ACTION', 'NOTES', 'RCL_CMPT_ID',
    'COL_24', 'COL_25', 'COL_26', 'COL_27', 'COL_28'
]

def parse_and_filter_recalls():
    zip_path = RAW_DIR / "FLAT_RCL_POST_2010.zip"
    print(f"Loading official recalls from {zip_path}...")
    df = pd.read_csv(
        zip_path,
        sep='\t',
        names=RECALL_COLS_29,
        encoding='latin1',
        on_bad_lines='skip',
        dtype=str
    )
    df['MAKE_CLEAN'] = df['MAKETXT'].astype(str).str.strip().str.upper()
    df['MODEL_CLEAN'] = df['MODELTXT'].astype(str).str.strip().str.upper()
    df['YEAR_CLEAN'] = pd.to_numeric(df['YEARTXT'], errors='coerce')
    df['COMP_CLEAN'] = df['COMPNAME'].astype(str).str.strip().str.upper()
    df['RECALL_DATE'] = pd.to_datetime(df['ODATE'].astype(str), format='%Y%m%d', errors='coerce')
    
    target_makes = ["FORD", "HONDA", "CHEVROLET", "TOYOTA", "TESLA"]
    df_filtered = df[df['MAKE_CLEAN'].isin(target_makes)].copy()
    
    out_file = PROCESSED_DIR / "real_nhtsa_recalls.parquet"
    df_filtered.to_parquet(out_file, index=False)
    print(f"Successfully saved {len(df_filtered)} official recalls for target manufacturers to {out_file}")
    
    # Print sample of Ford Explorer and Chevy Bolt recalls
    ford_sample = df_filtered[
        (df_filtered['MAKE_CLEAN'] == 'FORD') & 
        (df_filtered['MODEL_CLEAN'] == 'EXPLORER') & 
        (df_filtered['YEAR_CLEAN'] == 2016)
    ]
    print(f"Found {len(ford_sample)} official recalls for 2016 Ford Explorer:")
    for _, r in ford_sample[['CAMPNO', 'ODATE', 'COMP_CLEAN', 'DESC_DEFECT']].head(3).iterrows():
        print(f"  Campaign: {r['CAMPNO']} | Date: {r['ODATE']} | Comp: {r['COMP_CLEAN']}")
        print(f"  Summary: {str(r['DESC_DEFECT'])[:90]}...\n")

if __name__ == "__main__":
    parse_and_filter_recalls()
