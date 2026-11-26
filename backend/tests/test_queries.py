from datetime import date

import pytest
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app.db.models import Complaint, Entity, MonthlyFeature, Prediction, Recall
from app.queries import (
    AsOf, complaints_upto, features_upto, predictions_upto, recalls_known, resolve_as_of,
)


def test_as_of_parse_bounds():
    assert AsOf.parse("2019-04") == AsOf(date(2019, 4, 1), date(2019, 4, 30))
    assert AsOf.parse("2020-02").end == date(2020, 2, 29)
    assert AsOf.parse("2019-12").end == date(2019, 12, 31)
    assert AsOf.parse(date(2019, 4, 17)) == AsOf(date(2019, 4, 1), date(2019, 4, 30))
    assert AsOf.parse("2019-04").label == "2019-04"


@pytest.mark.parametrize("bad", ["2019-13", "2019-4", "201904", "2019-04-01", "", "abcd-ef"])
def test_as_of_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        AsOf.parse(bad)


@pytest.fixture
def boundary_rows(db):
    """Rows on both sides of the 2019-04 boundary."""
    with db.begin() as conn:
        fk = conn.scalar(insert(Entity).returning(Entity.id), {
            "entity_id": "ford_explorer_2016_suspension", "make": "FORD", "model": "EXPLORER",
            "model_year": 2016, "system": "SUSPENSION", "source": "nhtsa",
        })
        months = [date(2019, 3, 1), date(2019, 4, 1), date(2019, 5, 1)]
        conn.execute(insert(MonthlyFeature), [
            {"entity_fk": fk, "month": m, "complaints": i, "spike_flag": 0} for i, m in enumerate(months)
        ])
        conn.execute(insert(Prediction), [
            {"entity_fk": fk, "month": m, "model_version": "v1", "risk_score": 0.1 * i, "source": "nhtsa"}
            for i, m in enumerate(months)
        ])
        conn.execute(insert(Complaint), [
            {"cmplid": n, "entity_fk": fk, "complaint_date": d, "source": "nhtsa"}
            for n, d in enumerate([date(2019, 4, 1), date(2019, 4, 30), date(2019, 5, 1)], start=1)
        ])
        conn.execute(insert(Recall), [
            {"campno": c, "entity_fk": fk, "recall_date": d, "source": "nhtsa"}
            for c, d in [("19V001000", date(2019, 4, 30)), ("19V002000", date(2019, 5, 1))]
        ])
    return db


def test_no_future_rows_leak(boundary_rows):
    as_of = AsOf.parse("2019-04")
    with Session(boundary_rows) as s:
        months = s.scalars(features_upto(select(MonthlyFeature.month), as_of)).all()
        pred_months = s.scalars(predictions_upto(select(Prediction.month), as_of)).all()
        complaint_dates = s.scalars(complaints_upto(select(Complaint.complaint_date), as_of)).all()
        recall_dates = s.scalars(recalls_known(select(Recall.recall_date), as_of)).all()

    assert sorted(months) == [date(2019, 3, 1), date(2019, 4, 1)]
    assert sorted(pred_months) == [date(2019, 3, 1), date(2019, 4, 1)]
    assert sorted(complaint_dates) == [date(2019, 4, 1), date(2019, 4, 30)]
    assert recall_dates == [date(2019, 4, 30)]


def test_resolve_as_of(boundary_rows):
    with Session(boundary_rows) as s:
        assert resolve_as_of(s) == AsOf.parse("2019-05")
        assert resolve_as_of(s, "2019-04") == AsOf.parse("2019-04")


def test_resolve_as_of_empty(db):
    with Session(db) as s, pytest.raises(LookupError):
        resolve_as_of(s)
