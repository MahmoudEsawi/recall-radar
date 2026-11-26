"""
Single normalization for the group key (make + model + model_year + main system).
Every loader uses these functions so keys match across ML outputs and raw NHTSA files.
"""
import hashlib
import re
from datetime import date
from typing import Optional, Tuple

import pandas as pd

MISSING_TOKENS = frozenset({"", "NAN", "NONE", "NULL", "UNKNOWN"})
MIN_MODEL_YEAR = 1950
MAX_MODEL_YEAR = date.today().year + 2

_SPACES = r"\s+"
_YEAR = r"\d{4}(?:\.0+)?"

EntityKey = Tuple[str, str, int, str]


def _is_missing(value) -> bool:
    return value is None or (not isinstance(value, str) and pd.isna(value))


def clean_text(value) -> Optional[str]:
    if _is_missing(value):
        return None
    text = re.sub(_SPACES, " ", str(value)).strip().upper()
    return None if text in MISSING_TOKENS else text


def main_system(component) -> Optional[str]:
    """Part of the NHTSA component before the first ':'."""
    if _is_missing(component):
        return None
    return clean_text(str(component).split(":", 1)[0])


def clean_year(value) -> Optional[int]:
    """Four-digit model year within range, otherwise None."""
    if _is_missing(value):
        return None
    text = str(value).strip()
    if not re.fullmatch(_YEAR, text):
        return None
    year = int(text[:4])
    return year if MIN_MODEL_YEAR <= year <= MAX_MODEL_YEAR else None


def entity_key(make, model, model_year, component) -> Optional[EntityKey]:
    key = (clean_text(make), clean_text(model), clean_year(model_year), main_system(component))
    return None if any(part is None for part in key) else key


def entity_slug(make: str, model: str, model_year: int, system: str) -> str:
    raw = f"{make} {model} {model_year} {system}".lower()
    return re.sub(r"[^a-z0-9]+", "_", raw).strip("_")


def entity_slug_hashed(key: EntityKey) -> str:
    """Used when two keys produce the same slug, e.g. 'CR-V' and 'CR V'."""
    digest = hashlib.sha1("|".join(map(str, key)).encode("utf-8")).hexdigest()[:6]
    return f"{entity_slug(*key)}_{digest}"


def clean_text_series(values: pd.Series) -> pd.Series:
    text = values.astype("string").str.replace(_SPACES, " ", regex=True).str.strip().str.upper()
    return text.mask(text.isin(MISSING_TOKENS))


def main_system_series(values: pd.Series) -> pd.Series:
    return clean_text_series(values.astype("string").str.split(":", n=1).str[0])


def clean_year_series(values: pd.Series) -> pd.Series:
    text = values.astype("string").str.strip()
    valid = text.str.fullmatch(_YEAR).fillna(False).astype(bool)
    year = pd.to_numeric(text.str[:4].where(valid), errors="coerce").astype("Int64")
    return year.where((year >= MIN_MODEL_YEAR) & (year <= MAX_MODEL_YEAR))
