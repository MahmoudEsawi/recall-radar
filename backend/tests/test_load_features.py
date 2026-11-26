import tempfile
from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Entity, MonthlyFeature
from scripts.load_common import FEATURE_COLUMNS, LoadError
from scripts.load_features import load_features
from scripts.seed_mock import seed_mock

GROUPS = [
    ("  ford ", "Explorer", "2016", "SUSPENSION:REAR"),
    ("HONDA", "CR-V", "2017", "AIR BAGS"),
    ("HONDA", "CR V", "2017", "AIR BAGS"),
]
MONTHS = pd.date_range("2018-01-01", periods=14, freq="MS").strftime("%Y-%m-%d").tolist()


def _row(make, model, year, system, month, complaints=3, spike_flag=0, first_year=False):
    floats = None if first_year else 1.5
    return {
        "make": make, "model": model, "model_year": year, "system": system, "month": month,
        "complaints": complaints, "expected": floats, "spike_ratio": floats, "poisson_p": floats,
        "slope12": floats, "rel_slope12": floats, "spike_flag": spike_flag,
    }


def sample_frame() -> pd.DataFrame:
    """3 groups x 14 months of valid rows, then one row per rejection reason."""
    rows = [_row(*g, m, first_year=i < 12) for g in GROUPS for i, m in enumerate(MONTHS)]
    rows.append(dict(rows[-1]))  # duplicate key
    rows += [
        _row("unknown", "EXPLORER", "2016", "SUSPENSION", "2018-01-01"),
        _row("FORD", "EXPLORER", "16", "SUSPENSION", "2018-01-01"),
        _row("FORD", "EXPLORER", "9999", "SUSPENSION", "2018-01-01"),
        _row("FORD", "EXPLORER", "2016", ":REAR", "2018-01-01"),
        _row("FORD", "EXPLORER", "2016", "SUSPENSION", "2018-04-15"),
        _row("FORD", "EXPLORER", "2016", "SUSPENSION", "not a date"),
        _row("FORD", "EXPLORER", "2016", "SUSPENSION", "2018-01-01", complaints=-1),
        _row("FORD", "EXPLORER", "2016", "SUSPENSION", "2018-01-01", spike_flag=2),
    ]
    frame = pd.DataFrame(rows)
    assert list(frame.columns) == list(FEATURE_COLUMNS)
    return frame


EXPECTED_REJECTED = {
    "missing make": 1,
    "invalid model_year": 2,
    "missing system": 1,
    "month not first of month": 1,
    "invalid month": 1,
    "invalid complaints count": 1,
    "invalid spike_flag": 1,
    "duplicate key in file (first row kept)": 1,
}


@pytest.fixture
def sample_dir():
    """Generated sample files, outside the repo and deleted afterwards."""
    with tempfile.TemporaryDirectory(prefix="rr_sample_") as tmp:
        frame = sample_frame()
        frame.to_parquet(Path(tmp) / "monthly_features.parquet", index=False)
        frame.to_csv(Path(tmp) / "monthly_features.csv", index=False)
        yield Path(tmp)


def _counts(engine):
    with Session(engine) as s:
        return (s.scalar(select(func.count()).select_from(Entity)),
                s.scalar(select(func.count()).select_from(MonthlyFeature)))


def test_load_features_parquet_then_csv_is_idempotent(db, sample_dir):
    first = load_features(db, sample_dir / "monthly_features.parquet")
    assert first.read == 42 + 1 + 8
    assert first.inserted == 42 and first.updated == 0
    assert dict(first.rejected) == EXPECTED_REJECTED
    assert _counts(db) == (3, 42)

    with Session(db) as s:
        entities = s.execute(select(Entity.entity_id, Entity.make, Entity.model, Entity.system)).all()
        nulls = s.scalar(select(func.count()).select_from(MonthlyFeature)
                         .where(MonthlyFeature.expected.is_(None)))
    slugs = sorted(e.entity_id for e in entities)
    assert slugs[0] == "ford_explorer_2016_suspension"
    assert slugs[1] == "honda_cr_v_2017_air_bags"
    assert slugs[2].startswith("honda_cr_v_2017_air_bags_")
    assert ("FORD", "EXPLORER", "SUSPENSION") in {(e.make, e.model, e.system) for e in entities}
    assert nulls == 3 * 12

    for path in ("monthly_features.parquet", "monthly_features.csv"):
        again = load_features(db, sample_dir / path, chunksize=7)
        assert again.inserted == 0
        assert again.updated == 42
        assert dict(again.rejected) == EXPECTED_REJECTED  # duplicate now spans two chunks
        assert _counts(db) == (3, 42)


def test_load_features_refuses_while_mock_loaded(db, sample_dir):
    seed_mock(db)
    with pytest.raises(LoadError, match="Mock data is loaded"):
        load_features(db, sample_dir / "monthly_features.parquet")


def test_seed_mock_refuses_after_real_load(db, sample_dir):
    load_features(db, sample_dir / "monthly_features.parquet")
    with pytest.raises(LoadError, match="Real data is loaded"):
        seed_mock(db)
