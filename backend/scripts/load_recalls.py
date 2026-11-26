"""
Load recalls from data/raw/FLAT_RCL_POST_2010.zip (recall_date from RCDATE).
Only recalls matching an entity already in the DB are kept.
Run from backend/: python -m scripts.load_recalls [--dry-run]
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy.engine import Engine

from app.db.session import get_direct_engine
from scripts.load_common import (
    RECALL_RAW_COLUMNS, RECALLS_ZIP, EntityIndex, LoadError, LoadReport, add_common_args,
    clean_body_text, copy_upsert, count_lines, guard_no_mock, iter_raw, normalize_keys,
    parse_yyyymmdd, print_db_size,
)

DB_COLUMNS = ["campno", "entity_fk", "recall_date", "defect_summary", "source"]


def prepare(chunk: pd.DataFrame, report: LoadReport, index: EntityIndex) -> pd.DataFrame:
    df = normalize_keys(chunk, report, "component")

    campno = df["campno"].astype("string").str.strip().str.upper()
    df = report.reject(df, campno.isna() | (campno == ""), "missing CAMPNO")
    recall_date = parse_yyyymmdd(df["recall_date"])
    df = report.reject(df, recall_date.isna(), "invalid recall date (RCDATE)")

    entity_fk = index.lookup(df)
    df = report.reject(df, entity_fk.isna(), "no matching entity")

    return pd.DataFrame({
        "campno": campno.loc[df.index].astype(object),
        "entity_fk": entity_fk.loc[df.index].astype("int64"),
        "recall_date": recall_date.loc[df.index],
        "defect_summary": clean_body_text(df["defect_summary"]),
    })


def merge_campaign_rows(frame: pd.DataFrame) -> pd.DataFrame:
    """One row per campaign and entity: earliest date, first non-empty defect summary."""
    frame = frame.sort_values("recall_date")
    return (frame.groupby(["campno", "entity_fk"], as_index=False, sort=False)
            .agg(recall_date=("recall_date", "min"), defect_summary=("defect_summary", "first")))


def load_recalls(engine: Engine, zip_path: Path = RECALLS_ZIP, chunksize: int = 100_000,
                 rejects_out: Optional[Path] = None, dry_run: bool = False) -> LoadReport:
    report = LoadReport("recalls", rejects_out)

    with engine.connect() as conn:
        with conn.begin():
            if not dry_run:
                guard_no_mock(conn)
            index = EntityIndex.load(conn)
        if not len(index):
            raise LoadError("No entities in the DB. Run load_features first.")

        parts = []
        for chunk in iter_raw(zip_path, RECALL_RAW_COLUMNS, chunksize):
            report.read += len(chunk)
            parts.append(prepare(chunk, report, index))
        report.count_rejected("malformed line skipped by parser", count_lines(zip_path) - report.read)

        matched = pd.concat(parts) if parts else pd.DataFrame(columns=DB_COLUMNS)
        recalls = merge_campaign_rows(matched)
        recalls["recall_date"] = recalls["recall_date"].dt.date
        recalls["source"] = "nhtsa"
        report.notes.append(f"campaign rows merged into one per campaign and entity: {len(matched) - len(recalls):,}")
        report.notes.append(f"entities with recalls: {recalls['entity_fk'].nunique():,} of {len(index):,}")

        if dry_run or recalls.empty:
            if dry_run:
                report.notes.append(f"dry run: would load {len(recalls):,} rows, nothing written")
            report.print()
            return report

        with conn.begin():
            result = copy_upsert(conn, "recalls", DB_COLUMNS, recalls,
                                 conflict=["campno", "entity_fk"], prune_source="nhtsa")
        report.inserted, report.updated = result.inserted, result.updated
        report.notes.append(f"previously loaded recalls no longer matched, removed: {result.deleted:,}")
        report.print()
        with conn.begin():
            print_db_size(conn)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, default=RECALLS_ZIP, help="path to FLAT_RCL_POST_2010.zip")
    parser.add_argument("--dry-run", action="store_true", help="match and report without writing")
    add_common_args(parser, chunksize=100_000)
    args = parser.parse_args()
    try:
        load_recalls(get_direct_engine(), args.zip, args.chunksize, args.rejects_out, args.dry_run)
    except LoadError as exc:
        sys.exit(f"Error: {exc}")


if __name__ == "__main__":
    main()
