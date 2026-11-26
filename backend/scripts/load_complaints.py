"""
Load a capped sample of real complaints per entity from data/raw/FLAT_CMPL.zip.
Only entities already in the DB (from monthly_features) are kept.

Selection per entity: up to --per-year complaints per calendar year of DATEA
(crash/fire/injury/death first, then most recent), then at most --max-per-entity
in total, taken round-robin across years (newest first) so every period keeps excerpts.

Run from backend/: python -m scripts.load_complaints [--max-per-entity 20] [--per-year 3] [--dry-run]
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy.engine import Engine

from app.db.session import get_direct_engine
from scripts.load_common import (
    COMPLAINT_RAW_COLUMNS, COMPLAINT_TEXT_COLUMNS, COMPLAINTS_ZIP, EntityIndex, LoadError,
    LoadReport, add_common_args, clean_body_text, copy_upsert, count_lines, guard_no_mock,
    iter_raw, normalize_keys, parse_yyyymmdd, print_db_size,
)

DB_COLUMNS = ["cmplid", "odino", "entity_fk", "complaint_date", "cdescr",
              "crash", "fire", "injured", "deaths", "source"]
_SORT = ["entity_fk", "year", "severe", "complaint_date", "cmplid"]
_SORT_ASC = [True, True, False, False, False]


def _flag(values: pd.Series) -> pd.Series:
    upper = values.astype("string").str.strip().str.upper()
    return upper.map({"Y": True, "N": False}).astype("boolean")


def prepare(chunk: pd.DataFrame, report: LoadReport, index: EntityIndex) -> pd.DataFrame:
    df = normalize_keys(chunk, report, "component")

    cmplid = pd.to_numeric(df["cmplid"], errors="coerce")
    df = report.reject(df, cmplid.isna(), "invalid CMPLID")
    complaint_date = parse_yyyymmdd(df["complaint_date"])
    df = report.reject(df, complaint_date.isna(), "invalid complaint date (DATEA)")

    entity_fk = index.lookup(df)
    df = report.reject(df, entity_fk.isna(), "no matching entity")

    out = pd.DataFrame(index=df.index)
    out["cmplid"] = pd.to_numeric(df["cmplid"]).astype("int64")
    out["odino"] = pd.to_numeric(df["odino"], errors="coerce").astype("Int64")
    out["entity_fk"] = entity_fk.loc[df.index].astype("int64")
    out["complaint_date"] = complaint_date.loc[df.index]
    out["crash"] = _flag(df["crash"])
    out["fire"] = _flag(df["fire"])
    out["injured"] = pd.to_numeric(df["injured"], errors="coerce").astype("Int64")
    out["deaths"] = pd.to_numeric(df["deaths"], errors="coerce").astype("Int64")
    out["severe"] = (
        out["crash"].fillna(False) | out["fire"].fillna(False)
        | out["injured"].fillna(0).gt(0) | out["deaths"].fillna(0).gt(0)
    ).astype(bool)
    out["year"] = out["complaint_date"].dt.year
    return out


def keep_top_per_year(pool: pd.DataFrame, per_year: int) -> pd.DataFrame:
    pool = pool.sort_values(_SORT, ascending=_SORT_ASC)
    return pool.groupby(["entity_fk", "year"], sort=False).head(per_year)


def pick_per_entity(pool: pd.DataFrame, max_per_entity: int) -> pd.DataFrame:
    pool = pool.sort_values(_SORT, ascending=_SORT_ASC).copy()
    pool["rank_in_year"] = pool.groupby(["entity_fk", "year"]).cumcount()
    pool = pool.sort_values(["entity_fk", "rank_in_year", "year"], ascending=[True, True, False])
    return pool.groupby("entity_fk", sort=False).head(max_per_entity)


def load_complaints(engine: Engine, zip_path: Path = COMPLAINTS_ZIP, max_per_entity: int = 20,
                    per_year: int = 3, chunksize: int = 200_000, rejects_out: Optional[Path] = None,
                    dry_run: bool = False) -> LoadReport:
    report = LoadReport("complaints", rejects_out)

    with engine.connect() as conn:
        with conn.begin():
            if not dry_run:
                guard_no_mock(conn)
            index = EntityIndex.load(conn)
        if not len(index):
            raise LoadError("No entities in the DB. Run load_features first.")

        print("Pass 1: selecting complaints...")
        pool = None
        for chunk in iter_raw(zip_path, COMPLAINT_RAW_COLUMNS, chunksize):
            report.read += len(chunk)
            df = prepare(chunk, report, index)
            if pool is not None:
                df = pd.concat([pool, df])
            dup = df.duplicated("cmplid", keep="first")
            df = report.reject(df, dup, "duplicate CMPLID")
            pool = keep_top_per_year(df, per_year)
        report.count_rejected("malformed line skipped by parser", count_lines(zip_path) - report.read)

        selected = pick_per_entity(pool, max_per_entity) if pool is not None else pd.DataFrame()
        report.notes.append(f"selection cap: {max_per_entity} per entity, {per_year} per entity per year")
        report.notes.append(f"entities with complaints: {selected['entity_fk'].nunique() if len(selected) else 0:,} "
                            f"of {len(index):,}")
        if selected.empty:
            report.print()
            return report

        print(f"Pass 2: reading text for {len(selected):,} complaints...")
        wanted = set(selected["cmplid"].tolist())
        texts = {}
        for chunk in iter_raw(zip_path, COMPLAINT_TEXT_COLUMNS, chunksize):
            ids = pd.to_numeric(chunk["cmplid"], errors="coerce")
            hit = ids.isin(wanted)
            texts.update(zip(ids[hit].astype("int64"), chunk.loc[hit, "cdescr"]))
        selected = selected.copy()
        selected["cdescr"] = clean_body_text(selected["cmplid"].map(texts))
        selected["complaint_date"] = selected["complaint_date"].dt.date
        selected["source"] = "nhtsa"
        report.notes.append(f"complaints without text: {int(selected['cdescr'].isna().sum()):,}")

        if dry_run:
            text_mb = selected["cdescr"].dropna().str.len().sum() / 1024 ** 2
            report.notes.append(f"dry run: would load {len(selected):,} rows (~{text_mb:.1f} MB of text), nothing written")
            report.print()
            return report

        with conn.begin():
            result = copy_upsert(conn, "complaints", DB_COLUMNS, selected,
                                 conflict=["cmplid"], prune_source="nhtsa")
        report.inserted, report.updated = result.inserted, result.updated
        report.notes.append(f"previously loaded complaints no longer selected, removed: {result.deleted:,}")
        report.print()
        with conn.begin():
            print_db_size(conn)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--zip", type=Path, default=COMPLAINTS_ZIP, help="path to FLAT_CMPL.zip")
    parser.add_argument("--max-per-entity", type=int, default=20)
    parser.add_argument("--per-year", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true", help="select and report without writing")
    add_common_args(parser, chunksize=200_000)
    args = parser.parse_args()
    try:
        load_complaints(get_direct_engine(), args.zip, args.max_per_entity, args.per_year,
                        args.chunksize, args.rejects_out, args.dry_run)
    except LoadError as exc:
        sys.exit(f"Error: {exc}")


if __name__ == "__main__":
    main()
