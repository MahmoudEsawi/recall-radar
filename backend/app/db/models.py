from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    JSON, BigInteger, Boolean, CheckConstraint, Date, DateTime, Double, ForeignKey,
    Index, Integer, SmallInteger, String, Text, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SOURCES = ("nhtsa", "mock")
_SOURCE_CHECK = "source IN ('nhtsa', 'mock')"
_JSON = JSON().with_variant(JSONB(), "postgresql")


class Base(DeclarativeBase):
    pass


def _entity_fk() -> Mapped[int]:
    return mapped_column(ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True)


class Entity(Base):
    """One complaint group: make + model + model_year + main system."""
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[str] = mapped_column(String(200), unique=True)
    make: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(100))
    model_year: Mapped[int] = mapped_column(SmallInteger)
    system: Mapped[str] = mapped_column(String(200))
    source: Mapped[str] = mapped_column(String(10), default="nhtsa")

    __table_args__ = (
        UniqueConstraint("make", "model", "model_year", "system", name="uq_entities_key"),
        CheckConstraint("model_year BETWEEN 1900 AND 2100", name="ck_entities_model_year"),
        CheckConstraint(_SOURCE_CHECK, name="ck_entities_source"),
        Index("ix_entities_make", "make"),
    )


class MonthlyFeature(Base):
    __tablename__ = "monthly_features"

    entity_fk: Mapped[int] = _entity_fk()
    month: Mapped[date] = mapped_column(Date, primary_key=True)
    complaints: Mapped[int] = mapped_column(Integer)
    expected: Mapped[Optional[float]] = mapped_column(Double)
    spike_ratio: Mapped[Optional[float]] = mapped_column(Double)
    poisson_p: Mapped[Optional[float]] = mapped_column(Double)
    slope12: Mapped[Optional[float]] = mapped_column(Double)
    rel_slope12: Mapped[Optional[float]] = mapped_column(Double)
    spike_flag: Mapped[Optional[int]] = mapped_column(SmallInteger)

    __table_args__ = (
        CheckConstraint("EXTRACT(DAY FROM month) = 1", name="ck_monthly_features_month"),
        CheckConstraint("complaints >= 0", name="ck_monthly_features_complaints"),
        CheckConstraint("spike_flag IN (0, 1)", name="ck_monthly_features_spike_flag"),
        Index("ix_monthly_features_month_spike", "month", "spike_flag", "spike_ratio"),
    )


class Prediction(Base):
    """Model output per entity per month. Score fields stay null until a model exists."""
    __tablename__ = "predictions"

    entity_fk: Mapped[int] = _entity_fk()
    month: Mapped[date] = mapped_column(Date, primary_key=True)
    model_version: Mapped[str] = mapped_column(String(100), primary_key=True)
    risk_score: Mapped[Optional[float]] = mapped_column(Double)
    risk_category: Mapped[Optional[str]] = mapped_column(String(20))
    predicted_recall_12m: Mapped[Optional[bool]] = mapped_column(Boolean)
    top_risk_factors: Mapped[Optional[list]] = mapped_column(_JSON)
    source: Mapped[str] = mapped_column(String(10), default="nhtsa")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("EXTRACT(DAY FROM month) = 1", name="ck_predictions_month"),
        CheckConstraint(_SOURCE_CHECK, name="ck_predictions_source"),
        Index("ix_predictions_month_score", "month", "risk_score"),
    )


class Complaint(Base):
    __tablename__ = "complaints"

    cmplid: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    odino: Mapped[Optional[int]] = mapped_column(BigInteger, index=True)
    entity_fk: Mapped[int] = mapped_column(ForeignKey("entities.id", ondelete="CASCADE"))
    complaint_date: Mapped[date] = mapped_column(Date)
    cdescr: Mapped[Optional[str]] = mapped_column(Text)
    crash: Mapped[Optional[bool]] = mapped_column(Boolean)
    fire: Mapped[Optional[bool]] = mapped_column(Boolean)
    injured: Mapped[Optional[int]] = mapped_column(Integer)
    deaths: Mapped[Optional[int]] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(10), default="nhtsa")

    __table_args__ = (
        CheckConstraint(_SOURCE_CHECK, name="ck_complaints_source"),
        Index("ix_complaints_entity_date", "entity_fk", "complaint_date"),
    )


class Recall(Base):
    __tablename__ = "recalls"

    campno: Mapped[str] = mapped_column(String(20), primary_key=True)
    entity_fk: Mapped[int] = _entity_fk()
    recall_date: Mapped[date] = mapped_column(Date)
    defect_summary: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(10), default="nhtsa")

    __table_args__ = (
        CheckConstraint(_SOURCE_CHECK, name="ck_recalls_source"),
        Index("ix_recalls_entity_date", "entity_fk", "recall_date"),
    )


class ModelResult(Base):
    """Evaluation metrics per model. Definitions are set by the ML team; extra_metrics holds anything else."""
    __tablename__ = "model_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(100))
    model_version: Mapped[str] = mapped_column(String(100))
    eval_start: Mapped[Optional[date]] = mapped_column(Date)
    eval_end: Mapped[Optional[date]] = mapped_column(Date)
    k: Mapped[Optional[int]] = mapped_column(Integer)
    pr_auc: Mapped[Optional[float]] = mapped_column(Double)
    roc_auc: Mapped[Optional[float]] = mapped_column(Double)
    precision_at_k: Mapped[Optional[float]] = mapped_column(Double)
    false_alerts_per_month: Mapped[Optional[float]] = mapped_column(Double)
    median_lead_time_months: Mapped[Optional[float]] = mapped_column(Double)
    extra_metrics: Mapped[Optional[dict]] = mapped_column(_JSON)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(10), default="nhtsa")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "model_name", "model_version", "k",
            name="uq_model_results_model_k", postgresql_nulls_not_distinct=True,
        ),
        CheckConstraint(_SOURCE_CHECK, name="ck_model_results_source"),
    )
