"""
Load monthly group features (data contract in backend/README.md).
Run from backend/: python -m scripts.load_features [--path FILE]
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy.engine import Engine

from app.db.session import get_direct_engine
from scripts.load_common import (
    FEATURE_COLUMNS, KEY_COLUMNS, PROCESSED_DIR, EntityIndex, LoadError, LoadReport,
    add_common_args, copy_upsert, guard_no_mock, iter_table, normalize_keys, print_db_size,
    start_run_dedupe,
)

FLOAT_COLUMNS = ["expected", "spike_ratio", "poisson_p", "slope12", "rel_slope12"]
DB_COLUMNS = ["entity_fk", "month", "complaints", *FLOAT_COLUMNS, "spike_flag"]
CONFLICT = ["entity_fk", "month"]
DUPLICATE_REASON = "duplicate key in file (first row kept)"


def default_path() -> Path:
    parquet = PROCESSED_DIR / "monthly_features.parquet"
    return parquet if parquet.exists() else PROCESSED_DIR / "monthly_features.csv"


def _blank(values: pd.Series) -> pd.Series:
    return values.isna() | (values.astype("string").str.strip() == "")


def prepare(chunk: pd.DataFrame, report: LoadReport) -> pd.DataFrame:
    df = chunk.rename(columns=FEATURE_COLUMNS)
    df = normalize_keys(df, report, "system")

    raw_month = df["month"]
    if pd.api.types.is_object_dtype(raw_month) or pd.api.types.is_string_dtype(raw_month):
        month = pd.to_datetime(raw_month.astype("string").str.strip(), format="ISO8601", errors="coerce")
    else:
        month = pd.to_datetime(raw_month, errors="coerce")
    df = report.reject(df, month.isna(), "invalid month")
    month = month.loc[df.index]
    df = report.reject(df, (month.dt.day != 1) | (month != month.dt.normalize()),
                       "month not first of month")

    complaints = pd.to_numeric(df["complaints"], errors="coerce")
    df = report.reject(df, complaints.isna() | (complaints < 0) | (complaints % 1 != 0),
                       "invalid complaints count")

    for col in FLOAT_COLUMNS:
        values = pd.to_numeric(df[col], errors="coerce")
        df = report.reject(df, values.isna() & ~_blank(df[col]), f"invalid {col}")

    spike = pd.to_numeric(df["spike_flag"], errors="coerce")
    df = report.reject(df, ~spike.isin([0, 1]), "invalid spike_flag")

    out = df[KEY_COLUMNS].copy()
    out["month"] = month.loc[df.index].dt.date
    out["complaints"] = pd.to_numeric(df["complaints"]).astype("Int64")
    for col in FLOAT_COLUMNS:
        out[col] = pd.to_numeric(df[col], errors="coerce").astype(float)
    out["spike_flag"] = pd.to_numeric(df["spike_flag"]).astype("Int64")

    dup = out.duplicated(KEY_COLUMNS + ["month"], keep="first")
    return report.reject(out, dup, DUPLICATE_REASON)


def load_features(engine: Engine, path: Path, chunksize: int = 50_000,
                  rejects_out: Optional[Path] = None) -> LoadReport:
    path = Path(path)
    if not path.exists():
        raise LoadError(f"{path} not found")
    report = LoadReport("monthly_features", rejects_out)

    with engine.connect() as conn:
        with conn.begin():
            guard_no_mock(conn)
            index = EntityIndex.load(conn)
            start_run_dedupe(conn, "monthly_features", CONFLICT)

        for chunk in iter_table(path, list(FEATURE_COLUMNS), chunksize):
            report.read += len(chunk)
            df = prepare(chunk, report)
            if df.empty:
                continue
            with conn.begin():
                df["entity_fk"] = index.ensure(conn, df)
                result = copy_upsert(conn, "monthly_features", DB_COLUMNS, df,
                                     conflict=CONFLICT, run_dedupe=True)
            report.inserted += result.inserted
            report.updated += result.updated
            report.count_rejected(DUPLICATE_REASON, result.duplicates)

        report.notes.append(f"new entities: {index.created:,} (total {len(index):,})")
        if index.hashed_slugs:
            report.notes.append(f"entity slugs given a hash suffix to avoid a collision: {index.hashed_slugs:,}")
        report.print()
        with conn.begin():
            print_db_size(conn)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=None, help="monthly_features .parquet or .csv")
    add_common_args(parser, chunksize=50_000)
    args = parser.parse_args()
    try:
        load_features(get_direct_engine(), args.path or default_path(), args.chunksize, args.rejects_out)
    except LoadError as exc:
        sys.exit(f"Error: {exc}")


if __name__ == "__main__":
    main()
