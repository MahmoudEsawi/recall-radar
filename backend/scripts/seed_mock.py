"""
Seed the DB with the MOCK data from app/mock_data.py so the API works before real data is loaded.
Every row is stored with source='mock'. Complaint IDs are negative so they can't clash with NHTSA IDs.
Refuses to run once real data is loaded.

Run from backend/: python -m scripts.seed_mock          (reseed mock data)
                   python -m scripts.seed_mock --clear  (remove all mock data)
"""
import argparse
import sys
from datetime import date

from sqlalchemy import delete, func, insert, select
from sqlalchemy.engine import Connection, Engine

from app.db.models import Complaint, Entity, MonthlyFeature, Prediction, Recall
from app.db.session import get_direct_engine
from app.entity_key import entity_key
from app.mock_data import MOCK_ALERTS, MOCK_TIME_MACHINE
from scripts.load_common import LoadError, print_db_size

MOCK = "mock"
MOCK_MODEL_VERSION = "mock"


def _month(value: str) -> date:
    return date.fromisoformat(value[:7] + "-01")


def clear_mock(conn: Connection) -> int:
    for model in (Prediction, Complaint, Recall):
        conn.execute(delete(model).where(model.source == MOCK))
    return conn.execute(delete(Entity).where(Entity.source == MOCK)).rowcount


def seed_mock(engine: Engine) -> dict:
    with engine.begin() as conn:
        real = conn.scalar(select(func.count()).select_from(Entity).where(Entity.source != MOCK))
        if real:
            raise LoadError("Real data is loaded; mock seed skipped. Use --clear to remove old mock rows.")
        clear_mock(conn)

        ids = {}
        for alert in MOCK_ALERTS:
            make, model, year, system = entity_key(alert["make"], alert["model"], alert["year"], alert["component"])
            ids[alert["entity_id"]] = conn.scalar(insert(Entity).returning(Entity.id), {
                "entity_id": alert["entity_id"], "make": make, "model": model,
                "model_year": year, "system": system, "source": MOCK,
            })

        predictions, features = {}, []
        for entity_id, sim in MOCK_TIME_MACHINE.items():
            previous = 0
            for point in sim["monthly_timeline"]:
                month = _month(point["month"])
                predictions[(entity_id, month)] = {"risk_score": point["risk_score"]}
                # Mock timeline counts are cumulative; store the monthly increase.
                features.append({"entity_fk": ids[entity_id], "month": month,
                                 "complaints": point["complaints"] - previous})
                previous = point["complaints"]

        for alert in MOCK_ALERTS:
            predictions[(alert["entity_id"], _month(alert["as_of_date"]))] = {
                "risk_score": alert["risk_score"],
                "risk_category": alert["risk_category"],
                "predicted_recall_12m": alert["predicted_recall_within_12m"],
                "top_risk_factors": alert["top_risk_factors"],
            }

        prediction_rows = [
            {"entity_fk": ids[entity_id], "month": month, "model_version": MOCK_MODEL_VERSION,
             "risk_score": None, "risk_category": None, "predicted_recall_12m": None,
             "top_risk_factors": None, "source": MOCK, **values}
            for (entity_id, month), values in predictions.items()
        ]

        complaint_rows, recall_rows = [], []
        for alert in MOCK_ALERTS:
            for text in alert.get("sample_complaints", []):
                complaint_rows.append({
                    "cmplid": -(len(complaint_rows) + 1), "odino": None,
                    "entity_fk": ids[alert["entity_id"]], "complaint_date": _month(alert["as_of_date"]),
                    "cdescr": text, "crash": None, "fire": None, "injured": None, "deaths": None,
                    "source": MOCK,
                })
            recall = alert.get("official_recall")
            if recall and recall.get("recalled"):
                recall_rows.append({
                    "campno": recall["campaign_id"], "entity_fk": ids[alert["entity_id"]],
                    "recall_date": date.fromisoformat(recall["recall_date"]),
                    "defect_summary": recall["defect_summary"], "source": MOCK,
                })

        for model, rows in ((MonthlyFeature, features), (Prediction, prediction_rows),
                            (Complaint, complaint_rows), (Recall, recall_rows)):
            if rows:
                conn.execute(insert(model), rows)

    return {"entities": len(ids), "monthly_features": len(features), "predictions": len(prediction_rows),
            "complaints": len(complaint_rows), "recalls": len(recall_rows)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--clear", action="store_true", help="remove all mock rows and exit")
    args = parser.parse_args()
    engine = get_direct_engine()
    try:
        if args.clear:
            with engine.begin() as conn:
                print(f"Removed {clear_mock(conn)} mock entities and their rows.")
        else:
            counts = seed_mock(engine)
            print("Seeded MOCK data (source='mock'):", ", ".join(f"{k}={v}" for k, v in counts.items()))
    except LoadError as exc:
        sys.exit(f"Error: {exc}")
    with engine.connect() as conn:
        print_db_size(conn)


if __name__ == "__main__":
    main()
