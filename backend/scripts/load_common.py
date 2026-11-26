"""
Shared pieces for the loaders: source column maps, chunked readers, entity lookup,
staging + upsert, rejection report and DB size report.
"""
import csv
import io
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence

import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import func, insert, select, text
from sqlalchemy.engine import Connection

from app.db.models import Entity
from app.entity_key import (
    EntityKey, clean_text_series, clean_year_series, entity_slug, entity_slug_hashed,
    main_system_series,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
RAW_DIR = REPO_ROOT / "data" / "raw"

KEY_COLUMNS = ["make", "model", "model_year", "system"]

# Source column -> internal name. An upstream rename is a one-line change here.
FEATURE_COLUMNS = {
    "make": "make",
    "model": "model",
    "model_year": "model_year",
    "system": "system",
    "month": "month",
    "complaints": "complaints",
    "expected": "expected",
    "spike_ratio": "spike_ratio",
    "poisson_p": "poisson_p",
    "slope12": "slope12",
    "rel_slope12": "rel_slope12",
    "spike_flag": "spike_flag",
}

# FLAT_CMPL.txt has no header; positions follow the NHTSA layout (CMPL.txt).
COMPLAINT_RAW_COLUMNS = {
    0: "cmplid",
    1: "odino",
    3: "make",
    4: "model",
    5: "model_year",
    6: "crash",
    8: "fire",
    9: "injured",
    10: "deaths",
    11: "component",
    15: "complaint_date",  # DATEA
}
COMPLAINT_TEXT_COLUMNS = {0: "cmplid", 19: "cdescr"}

# FLAT_RCL_POST_2010.txt, positions follow the NHTSA layout (RCL.txt).
RECALL_RAW_COLUMNS = {
    1: "campno",
    2: "make",
    3: "model",
    4: "model_year",
    6: "component",
    15: "recall_date",  # RCDATE
    19: "defect_summary",
}

COMPLAINTS_ZIP = RAW_DIR / "FLAT_CMPL.zip"
RECALLS_ZIP = RAW_DIR / "FLAT_RCL_POST_2010.zip"

DB_TABLES = ["entities", "monthly_features", "predictions", "complaints", "recalls", "model_results"]


class LoadError(RuntimeError):
    pass


class LoadReport:
    def __init__(self, name: str, rejects_out: Optional[Path] = None):
        self.name = name
        self.read = 0
        self.inserted = 0
        self.updated = 0
        self.rejected: Counter = Counter()
        self.notes: List[str] = []
        self.rejects_out = rejects_out
        self._rejects_header = True

    @property
    def loaded(self) -> int:
        return self.inserted + self.updated

    def count_rejected(self, reason: str, n: int) -> None:
        if n > 0:
            self.rejected[reason] += n

    def reject(self, frame: pd.DataFrame, mask: pd.Series, reason: str) -> pd.DataFrame:
        """Drop rows where mask is true, count them under reason, return the rest."""
        bad = mask.reindex(frame.index, fill_value=False).fillna(False).astype(bool)
        n = int(bad.sum())
        if n:
            self.rejected[reason] += n
            if self.rejects_out:
                frame[bad].assign(reject_reason=reason).to_csv(
                    self.rejects_out, mode="a", index=False, header=self._rejects_header,
                )
                self._rejects_header = False
        return frame[~bad]

    def print(self) -> None:
        print(f"{self.name}: read={self.read:,} loaded={self.loaded:,} "
              f"(inserted={self.inserted:,} updated={self.updated:,}) "
              f"rejected={sum(self.rejected.values()):,}")
        for reason, n in self.rejected.most_common():
            print(f"  rejected  {reason}: {n:,}")
        for note in self.notes:
            print(f"  note      {note}")


def iter_table(path: Path, columns: Sequence[str], chunksize: int) -> Iterator[pd.DataFrame]:
    """Chunked read of a parquet or CSV file, only the given columns."""
    path = Path(path)
    if path.suffix == ".parquet":
        pf = pq.ParquetFile(path)
        _require_columns(path, columns, pf.schema_arrow.names)
        for batch in pf.iter_batches(batch_size=chunksize, columns=list(columns)):
            yield batch.to_pandas()
    elif path.suffix == ".csv":
        _require_columns(path, columns, pd.read_csv(path, nrows=0).columns)
        yield from pd.read_csv(path, usecols=list(columns), dtype=str, chunksize=chunksize)
    else:
        raise LoadError(f"Unsupported file type: {path.name} (expected .parquet or .csv)")


def _require_columns(path: Path, columns: Sequence[str], available) -> None:
    missing = sorted(set(columns) - set(available))
    if missing:
        raise LoadError(f"{path.name} is missing columns: {', '.join(missing)}")


def iter_raw(zip_path: Path, columns: Dict[int, str], chunksize: int) -> Iterator[pd.DataFrame]:
    """Chunked read of a headerless, tab-separated NHTSA flat file inside its zip."""
    if not Path(zip_path).exists():
        raise LoadError(f"{zip_path} not found. Download it from NHTSA into data/raw/.")
    reader = pd.read_csv(
        zip_path, sep="\t", header=None, usecols=list(columns), dtype=str,
        encoding="latin-1", quoting=csv.QUOTE_NONE, on_bad_lines="skip", chunksize=chunksize,
    )
    for chunk in reader:
        yield chunk.rename(columns=columns)


def count_lines(zip_path: Path) -> int:
    with zipfile.ZipFile(zip_path) as zf, zf.open(zf.infolist()[0]) as f:
        return sum(block.count(b"\n") for block in iter(lambda: f.read(1 << 24), b""))


def normalize_keys(frame: pd.DataFrame, report: LoadReport, system_column: str) -> pd.DataFrame:
    """Clean the group key columns in place of the raw ones; reject rows with a missing or invalid part."""
    make = clean_text_series(frame["make"])
    model = clean_text_series(frame["model"])
    year = clean_year_series(frame["model_year"])
    system = main_system_series(frame[system_column])

    for mask, reason in [
        (make.isna(), "missing make"),
        (model.isna(), "missing model"),
        (year.isna(), "invalid model_year"),
        (system.isna(), "missing system"),
    ]:
        frame = report.reject(frame, mask, reason)

    frame = frame.copy()
    frame["make"] = make.loc[frame.index].astype(object)
    frame["model"] = model.loc[frame.index].astype(object)
    frame["model_year"] = year.loc[frame.index].astype(int)
    frame["system"] = system.loc[frame.index].astype(object)
    return frame


def parse_yyyymmdd(values: pd.Series) -> pd.Series:
    return pd.to_datetime(values, format="%Y%m%d", errors="coerce")


def clean_body_text(values: pd.Series) -> pd.Series:
    stripped = values.astype("string").str.strip()
    return stripped.mask(stripped == "").astype(object)


def guard_no_mock(conn: Connection) -> None:
    n = conn.scalar(select(func.count()).select_from(Entity).where(Entity.source == "mock"))
    if n:
        raise LoadError("Mock data is loaded. Run python -m scripts.seed_mock --clear before loading real data.")


class EntityIndex:
    """In-memory map of group key -> entities.id for one loader run."""

    def __init__(self):
        self.ids: Dict[EntityKey, int] = {}
        self.slugs: set = set()
        self.created = 0
        self.hashed_slugs = 0

    @classmethod
    def load(cls, conn: Connection) -> "EntityIndex":
        index = cls()
        rows = conn.execute(select(Entity.id, Entity.entity_id, *[getattr(Entity, c) for c in KEY_COLUMNS]))
        for row in rows:
            index.ids[(row.make, row.model, row.model_year, row.system)] = row.id
            index.slugs.add(row.entity_id)
        return index

    def __len__(self) -> int:
        return len(self.ids)

    @staticmethod
    def _keys(frame: pd.DataFrame) -> List[EntityKey]:
        return list(zip(frame["make"], frame["model"], frame["model_year"].astype(int), frame["system"]))

    def lookup(self, frame: pd.DataFrame) -> pd.Series:
        """entities.id per row, NA where the group isn't loaded."""
        ids = [self.ids.get(key) for key in self._keys(frame)]
        return pd.Series(ids, index=frame.index, dtype="Int64")

    def ensure(self, conn: Connection, frame: pd.DataFrame, source: str = "nhtsa") -> pd.Series:
        """Like lookup, but creates missing entities first."""
        new_rows = []
        for key in dict.fromkeys(self._keys(frame)):
            if key in self.ids:
                continue
            slug = entity_slug(*key)
            if slug in self.slugs:
                slug = entity_slug_hashed(key)
                self.hashed_slugs += 1
            if slug in self.slugs:
                raise LoadError(f"Entity slug collision could not be resolved for {key}")
            self.slugs.add(slug)
            new_rows.append(dict(zip(["entity_id", *KEY_COLUMNS, "source"], [slug, *key, source])))

        if new_rows:
            stmt = insert(Entity).returning(Entity.id, *[getattr(Entity, c) for c in KEY_COLUMNS],
                                            sort_by_parameter_order=True)
            for row in conn.execute(stmt, new_rows):
                self.ids[(row.make, row.model, row.model_year, row.system)] = row.id
            self.created += len(new_rows)
        return self.lookup(frame)


@dataclass
class UpsertResult:
    inserted: int = 0
    updated: int = 0
    deleted: int = 0
    duplicates: int = 0


def start_run_dedupe(conn: Connection, table: str, conflict: Sequence[str]) -> None:
    """Track keys already written in this run, for files read in several chunks. Needs one connection per run."""
    seen = f"seen_{table}"
    keys = ", ".join(conflict)
    conn.exec_driver_sql(f"CREATE TEMP TABLE IF NOT EXISTS {seen} AS SELECT {keys} FROM {table} WITH NO DATA")
    conn.exec_driver_sql(f"CREATE UNIQUE INDEX IF NOT EXISTS {seen}_key ON {seen} ({keys})")
    conn.exec_driver_sql(f"TRUNCATE {seen}")


def copy_upsert(
    conn: Connection,
    table: str,
    columns: Sequence[str],
    frame: pd.DataFrame,
    conflict: Sequence[str],
    prune_source: Optional[str] = None,
    run_dedupe: bool = False,
    slice_rows: int = 50_000,
) -> UpsertResult:
    """
    COPY frame into a temp staging table, then INSERT ... ON CONFLICT DO UPDATE.
    run_dedupe drops rows whose key was already written earlier in the run (see start_run_dedupe).
    prune_source deletes rows of that source missing from frame (full replace).
    Must run inside a transaction.
    """
    result = UpsertResult()
    stage = f"stg_{table}"
    cols = ", ".join(columns)
    conn.exec_driver_sql(f"CREATE TEMP TABLE IF NOT EXISTS {stage} (LIKE {table} INCLUDING DEFAULTS)")
    conn.exec_driver_sql(f"TRUNCATE {stage}")

    with conn.connection.dbapi_connection.cursor() as cur:
        with cur.copy(f"COPY {stage} ({cols}) FROM STDIN WITH (FORMAT csv)") as copy:
            for start in range(0, len(frame), slice_rows):
                buf = io.StringIO()
                frame.iloc[start:start + slice_rows][list(columns)].to_csv(
                    buf, header=False, index=False, lineterminator="\n")
                copy.write(buf.getvalue())

    match = " AND ".join(f"s.{c} = t.{c}" for c in conflict)
    if run_dedupe:
        keys = ", ".join(conflict)
        result.duplicates = conn.exec_driver_sql(
            f"WITH fresh AS (INSERT INTO seen_{table} ({keys}) SELECT {keys} FROM {stage} "
            f"ON CONFLICT DO NOTHING RETURNING {keys}) "
            f"DELETE FROM {stage} s WHERE NOT EXISTS (SELECT 1 FROM fresh t WHERE {match})"
        ).rowcount

    updates = [c for c in columns if c not in conflict]
    set_clause = ", ".join(f"{c} = EXCLUDED.{c}" for c in updates)
    action = f"DO UPDATE SET {set_clause}" if updates else "DO NOTHING"
    flags = conn.exec_driver_sql(
        f"INSERT INTO {table} ({cols}) SELECT {cols} FROM {stage} "
        f"ON CONFLICT ({', '.join(conflict)}) {action} RETURNING (xmax = 0)"
    ).scalars().all()
    result.inserted = sum(1 for f in flags if f)
    result.updated = len(flags) - result.inserted

    if prune_source:
        result.deleted = conn.exec_driver_sql(
            f"DELETE FROM {table} t WHERE t.source = %(source)s "
            f"AND NOT EXISTS (SELECT 1 FROM {stage} s WHERE {match})",
            {"source": prune_source},
        ).rowcount
    return result


def _human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024


def print_db_size(conn: Connection) -> None:
    total = conn.scalar(text("SELECT pg_database_size(current_database())"))
    print(f"Database size: {_human(total)} (Neon free tier limit is 0.5 GB)")
    for table in DB_TABLES:
        size = conn.scalar(text("SELECT pg_total_relation_size(to_regclass(:t))"), {"t": table})
        if size is not None:
            print(f"  {table:<17} {_human(size)}")


def add_common_args(parser, chunksize: int) -> None:
    parser.add_argument("--chunksize", type=int, default=chunksize, help="rows per read chunk")
    parser.add_argument("--rejects-out", type=Path, default=None,
                        help="append rejected rows with their reason to this CSV")
