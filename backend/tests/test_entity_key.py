import pandas as pd
import pytest

from app.entity_key import (
    MAX_MODEL_YEAR, clean_text, clean_text_series, clean_year, clean_year_series, entity_key,
    entity_slug, entity_slug_hashed, main_system, main_system_series,
)

TEXT_CASES = [
    ("  ford ", "FORD"),
    ("Bolt   EV", "BOLT EV"),
    ("f-150\tsupercrew", "F-150 SUPERCREW"),
    ("", None),
    ("   ", None),
    ("nan", None),
    ("None", None),
    ("NULL", None),
    ("unknown", None),
    (None, None),
]

SYSTEM_CASES = [
    ("AIR BAGS:FRONTAL:DRIVER SIDE", "AIR BAGS"),
    ("fuel system, gasoline:delivery", "FUEL SYSTEM, GASOLINE"),
    ("SUSPENSION", "SUSPENSION"),
    (" electrical  system : wiring", "ELECTRICAL SYSTEM"),
    (":REAR", None),
    ("UNKNOWN OR OTHER", "UNKNOWN OR OTHER"),
    ("unknown:x", None),
    (None, None),
]

YEAR_CASES = [
    ("2016", 2016),
    (" 2016 ", 2016),
    (2016, 2016),
    ("2016.0", 2016),
    (2016.0, 2016),
    ("16", None),
    ("20161", None),
    ("20a6", None),
    ("9999", None),
    ("1949", None),
    ("1950", 1950),
    (str(MAX_MODEL_YEAR + 1), None),
    ("2016.5", None),
    (None, None),
]


@pytest.mark.parametrize("raw,expected", TEXT_CASES)
def test_clean_text(raw, expected):
    assert clean_text(raw) == expected


@pytest.mark.parametrize("raw,expected", SYSTEM_CASES)
def test_main_system(raw, expected):
    assert main_system(raw) == expected


@pytest.mark.parametrize("raw,expected", YEAR_CASES)
def test_clean_year(raw, expected):
    assert clean_year(raw) == expected


def _as_list(series):
    return [None if pd.isna(v) else v for v in series]


@pytest.mark.parametrize("scalar_fn,series_fn,cases", [
    (clean_text, clean_text_series, TEXT_CASES),
    (main_system, main_system_series, SYSTEM_CASES),
])
def test_series_matches_scalar(scalar_fn, series_fn, cases):
    raw = pd.Series([c[0] for c in cases], dtype=object)
    assert _as_list(series_fn(raw)) == [scalar_fn(c[0]) for c in cases]


def test_year_series_matches_scalar():
    string_cases = [c for c in YEAR_CASES if not isinstance(c[0], (int, float))]
    raw = pd.Series([c[0] for c in string_cases], dtype=object)
    assert _as_list(clean_year_series(raw)) == [c[1] for c in string_cases]
    assert _as_list(clean_year_series(pd.Series([2016, 1949], dtype="int64"))) == [2016, None]
    assert _as_list(clean_year_series(pd.Series([2016.0, None]))) == [2016, None]


def test_entity_key_rejects_any_missing_part():
    assert entity_key(" ford", "explorer", "2016", "SUSPENSION:REAR") == ("FORD", "EXPLORER", 2016, "SUSPENSION")
    assert entity_key("", "EXPLORER", "2016", "SUSPENSION") is None
    assert entity_key("FORD", "EXPLORER", "9999", "SUSPENSION") is None
    assert entity_key("FORD", "EXPLORER", "2016", "") is None


def test_slugs():
    assert entity_slug("FORD", "EXPLORER", 2016, "SUSPENSION") == "ford_explorer_2016_suspension"
    assert entity_slug("HONDA", "CR-V", 2017, "AIR BAGS") == "honda_cr_v_2017_air_bags"
    assert entity_slug("HONDA", "CR V", 2017, "AIR BAGS") == "honda_cr_v_2017_air_bags"
    hashed_a = entity_slug_hashed(("HONDA", "CR-V", 2017, "AIR BAGS"))
    hashed_b = entity_slug_hashed(("HONDA", "CR V", 2017, "AIR BAGS"))
    assert hashed_a != hashed_b
    assert hashed_a.startswith("honda_cr_v_2017_air_bags_")
