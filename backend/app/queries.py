"""
No-future-data rule. Every query that takes an as_of month goes through these filters:
monthly rows up to the as_of month, complaints and recalls up to the last day of that month.
"""
import calendar
import re
from dataclasses import dataclass
from datetime import date
from typing import Optional, Union

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.db.models import Complaint, MonthlyFeature, Prediction, Recall


@dataclass(frozen=True)
class AsOf:
    month: date  # first day of the as_of month
    end: date    # last day of the as_of month

    @classmethod
    def from_date(cls, value: date) -> "AsOf":
        last_day = calendar.monthrange(value.year, value.month)[1]
        return cls(month=value.replace(day=1), end=value.replace(day=last_day))

    @classmethod
    def parse(cls, value: Union[str, date]) -> "AsOf":
        """Accepts 'YYYY-MM' or a date."""
        if isinstance(value, date):
            return cls.from_date(value)
        match = re.fullmatch(r"(\d{4})-(\d{2})", value.strip())
        if not match or not 1 <= int(match.group(2)) <= 12:
            raise ValueError(f"as_of must be YYYY-MM, got {value!r}")
        return cls.from_date(date(int(match.group(1)), int(match.group(2)), 1))

    @property
    def label(self) -> str:
        return self.month.strftime("%Y-%m")


def resolve_as_of(db: Session, value: Optional[Union[str, date]] = None) -> AsOf:
    """Requested month, or the latest month in monthly_features when none is given."""
    if value is not None:
        return AsOf.parse(value)
    latest = db.scalar(select(func.max(MonthlyFeature.month)))
    if latest is None:
        raise LookupError("monthly_features is empty")
    return AsOf.from_date(latest)


def features_upto(stmt: Select, as_of: AsOf) -> Select:
    return stmt.where(MonthlyFeature.month <= as_of.month)


def predictions_upto(stmt: Select, as_of: AsOf) -> Select:
    return stmt.where(Prediction.month <= as_of.month)


def complaints_upto(stmt: Select, as_of: AsOf) -> Select:
    return stmt.where(Complaint.complaint_date <= as_of.end)


def recalls_known(stmt: Select, as_of: AsOf) -> Select:
    return stmt.where(Recall.recall_date <= as_of.end)
