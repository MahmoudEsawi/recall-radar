"""
Script to build a high-quality real NHTSA benchmark dataset
combining the official FLAT_RCL_POST_2010 recalls file and real complaints via NHTSA API.
"""

import json
import urllib.request
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

VEHICLE_FLEET = [
    {"make": "FORD", "model": "EXPLORER", "year": 2016},
    {"make": "HONDA", "model": "CIVIC", "year": 2017},
    {"make": "CHEVROLET", "model": "BOLT EV", "year": 2020},
    {"make": "TOYOTA", "model": "RAV4", "year": 2019},
    {"make": "TESLA", "model": "MODEL 3", "year": 2019}
]

RECALL_COLS = [
    'RECORD_ID', 'CAMPNO', 'MAKETXT', 'MODELTXT', 'YEARTXT', 
    'MFGCAMPNO', 'COMPNAME', 'MFGNAME', 'BGMAN', 'ENDMAN', 
    'RCLTYPECD', 'POTAFF', 'ODATE', 'INFLUENCED_BY', 'MFGTXT', 
    'RCDATE', 'DATEA', 'RPNO', 'FMVSS', 'DESC_DEFECT', 
    'CONEQUENCE_DEFECT', 'CORRECTIVE_ACTION', 'NOTES', 'RCL_CMPT_ID'
]


def load_real_recalls():
    zip_path = RAW_DIR / "FLAT_RCL_POST_2010.zip"
    print(f"Loading official recalls from {zip_path}...")
    df = pd.read_csv(
        zip_path,
        sep='\t',
        names=RECALL_COLS,
        encoding='latin1',
        on_bad_lines='skip',
        dtype={'YEARTXT': str}
    )
    df['MAKE_CLEAN'] = df['MAKETXT'].astype(str).str.strip().str.upper()
    df['MODEL_CLEAN'] = df['MODELTXT'].astype(str).str.strip().str.upper()
    df['YEAR_CLEAN'] = pd.to_numeric(df['YEARTXT'], errors='coerce')
    df['COMP_CLEAN'] = df['COMPNAME'].astype(str).str.strip().str.upper()
    df['RECALL_DATE'] = pd.to_datetime(df['BGMAN'].astype(str), format='%Y%m%d', errors='coerce')
    
    # Filter for our key fleet makes
    target_makes = ["FORD", "HONDA", "CHEVROLET", "TOYOTA", "TESLA"]
    df_filtered = df[df['MAKE_CLEAN'].isin(target_makes)].copy()
    
    out_file = PROCESSED_DIR / "real_nhtsa_recalls.parquet"
    df_filtered.to_parquet(out_file, index=False)
    print(f"Saved {len(df_filtered)} filtered official recalls to {out_file}")
    return df_filtered


def fetch_complaints_for_vehicle(make, model, year):
    encoded_model = urllib.parse.quote(model)
    url = f"https://api.nhtsa.gov/complaints/complaintsByVehicle?make={make}&model={encoded_model}&modelYear={year}"
    print(f"Fetching complaints for {year} {make} {model}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            results = data.get("results", [])
            print(f"  -> Found {len(results)} complaints.")
            records = []
            for r in results:
                records.append({
                    "odi_number": r.get("odiNumber"),
                    "make": make,
                    "model": model,
                    "year": year,
                    "crash": 1 if r.get("crash") else 0,
                    "fire": 1 if r.get("fire") else 0,
                    "injuries": r.get("numberOfInjuries", 0) or 0,
                    "deaths": r.get("numberOfDeaths", 0) or 0,
                    "date_filed": r.get("dateComplaintFiled"),
                    "components": r.get("components", ""),
                    "summary": r.get("summary", "")
                })
            return records
    except Exception as e:
        print(f"  -> Error fetching {make} {model}: {e}")
        return []


def main():
    recalls_df = load_real_recalls()
    
    all_complaints = []
    for veh in VEHICLE_FLEET:
        records = fetch_complaints_for_vehicle(veh["make"], veh["model"], veh["year"])
        all_complaints.extend(records)
        
    df_cmpl = pd.DataFrame(all_complaints)
    df_cmpl["date_filed"] = pd.to_datetime(df_cmpl["date_filed"], errors="coerce")
    df_cmpl["month"] = df_cmpl["date_filed"].dt.to_period("M").astype(str)
    
    cmpl_out = PROCESSED_DIR / "real_nhtsa_sample_complaints.parquet"
    df_cmpl.to_parquet(cmpl_out, index=False)
    print(f"\nSaved {len(df_cmpl)} real complaints to {cmpl_out}")

    # Build monthly aggregate per vehicle & primary component
    df_cmpl["primary_comp"] = df_cmpl["components"].str.split(",").str[0].str.strip().str.upper()
    monthly = df_cmpl.groupby(["make", "model", "year", "primary_comp", "month"]).agg(
        complaints_count=("odi_number", "count"),
        crash_count=("crash", "sum"),
        fire_count=("fire", "sum"),
        injury_count=("injuries", "sum")
    ).reset_index()

    monthly_out = PROCESSED_DIR / "real_vehicle_monthly_metrics.parquet"
    monthly.to_parquet(monthly_out, index=False)
    print(f"Saved monthly aggregated metrics to {monthly_out}")
    print("\nDataset preparation finished successfully!")


if __name__ == "__main__":
    main()

