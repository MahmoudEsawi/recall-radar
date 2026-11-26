# RecallRadar Backend API

Maintained by **Mahmoud & Faisal**.

Powered by **FastAPI** to serve real-time automotive defect risk assessments, fleet alerts, and the interactive Time Machine simulation.

## How to Run Locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Python 3.12 is recommended. With conda: `conda create -p <dir> python=3.12`, then `pip install -r requirements.txt` inside it.

- Interactive OpenAPI Swagger Docs: `http://localhost:8000/docs`
- ReDoc Docs: `http://localhost:8000/redoc`

## API Endpoints

- `GET /api/alerts`: List current high-risk vehicle/component clusters.
- `GET /api/timemachine/{entity_id}`: Monthly simulation data for time-slider playback.
- `GET /api/vehicles/{entity_id}`: Detailed investigation card for a specific vehicle defect.

## Database

PostgreSQL. The shared team database is on Neon (free tier, 0.5 GB); a local Postgres works the same way.

### Configuration

Copy `.env.example` to `backend/.env` (git-ignored) and fill in:

| Variable | Used by | Notes |
| :--- | :--- | :--- |
| `DATABASE_URL` | API | Pooled connection (Neon `-pooler` host). |
| `DIRECT_DATABASE_URL` | `init_db`, loaders, `seed_mock`, tests | Direct (non-pooled) connection. Staging temp tables and `COPY` need a session-level connection that PgBouncer transaction pooling can't guarantee. Falls back to `DATABASE_URL` when unset (local Postgres). |

Both accept `postgresql://` or `postgresql+psycopg://` URLs.

### Tables

| Table | Key | Content |
| :--- | :--- | :--- |
| `entities` | `id`; unique `entity_id` slug and unique (make, model, model_year, system) | One complaint group. |
| `monthly_features` | (entity_fk, month) | Monthly counts and spike/trend features from the time-series pipeline. |
| `predictions` | (entity_fk, month, model_version) | Model output. Score fields are nullable until a model exists. |
| `complaints` | `cmplid` | Capped sample of real NHTSA complaints per entity, with text and crash/fire/injury/death fields. |
| `recalls` | (campno, entity_fk) | NHTSA recall campaigns matched to entities. |
| `model_results` | `id`; unique (model_name, model_version, k) | Evaluation metrics per model. |

`entities`, `predictions`, `complaints`, `recalls` and `model_results` have a `source` column: `nhtsa` or `mock`.

### No-future-data rule

`app/queries.py` holds the only date filters for as-of queries. For an `as_of` month:

- `monthly_features` and `predictions`: `month <= as_of`
- `complaints`: `complaint_date <= last day of as_of month`
- `recalls`: known only if `recall_date <= last day of as_of month`

## Group key normalization

`app/entity_key.py`, used by every loader:

- Text: trim, uppercase, collapse repeated spaces.
- `""`, `NAN`, `NONE`, `NULL`, `UNKNOWN` are treated as missing; rows with any missing key part are rejected.
- `system`: the part of the NHTSA component before the first `:`.
- `model_year`: exactly 4 digits (`2016` or `2016.0`), between 1950 and the current year + 2. Anything else is rejected.
- `entity_id`: lowercase slug, e.g. `ford_explorer_2016_suspension`. If two keys give the same slug (`CR-V` and `CR V`), the later one gets a 6-character hash suffix.

## Data contract

### monthly_features (time-series pipeline output)

`data/processed/monthly_features.parquet` (or `.csv`). One row per group per month, unique on make + model + model_year + system + month.

| Column | Type | Rule |
| :--- | :--- | :--- |
| `make` | text | uppercase, trimmed |
| `model` | text | uppercase, trimmed |
| `model_year` | int | 4 digits |
| `system` | text | NHTSA component before the first `:` |
| `month` | date | first day of the month |
| `complaints` | int | complaints counted by DATEA, 0 for empty months |
| `expected` | float | nullable for each group's first 12 months |
| `spike_ratio` | float | nullable for each group's first 12 months |
| `poisson_p` | float | nullable for each group's first 12 months |
| `slope12` | float | nullable for each group's first 12 months |
| `rel_slope12` | float | nullable for each group's first 12 months |
| `spike_flag` | int | 0 or 1 |

Rows are rejected for: missing make/model/system, invalid model_year, invalid month, month not first of month, invalid complaints count (missing, negative or not whole), non-numeric float value, spike_flag not 0/1, duplicate key in the file (first row kept).

### Raw NHTSA files

Read directly from `data/raw/` (git-ignored), tab-separated, no header, latin-1. Download from NHTSA:

- `FLAT_CMPL.zip`: https://static.nhtsa.gov/odi/ffdd/cmpl/FLAT_CMPL.zip
- `FLAT_RCL_POST_2010.zip`: https://static.nhtsa.gov/odi/ffdd/rcl/FLAT_RCL_POST_2010.zip

| File | Columns used (0-based position) |
| :--- | :--- |
| `FLAT_CMPL.txt` | CMPLID (0), ODINO (1), MAKETXT (3), MODELTXT (4), YEARTXT (5), CRASH (6), FIRE (8), INJURED (9), DEATHS (10), COMPDESC (11), DATEA (15), CDESCR (19) |
| `FLAT_RCL_POST_2010.txt` | CAMPNO (1), MAKETXT (2), MODELTXT (3), YEARTXT (4), COMPNAME (6), RCDATE (15), DESC_DEFECT (19) |

Complaint dates use DATEA; recall dates use RCDATE. Column positions and names are mapped in one place: `scripts/load_common.py`.

## Loading data

Run from `backend/`. Every loader is an idempotent upsert, reads in chunks, and prints rows read, loaded (inserted/updated), rejected per reason, and the estimated DB size. `--rejects-out FILE.csv` writes rejected rows with their reason.

Load order:

```bash
python -m app.db.init_db                 # create tables
python -m scripts.seed_mock --clear      # remove mock rows (loaders refuse to run while they exist)
python -m scripts.load_features          # entities + monthly_features; --path to override the file
python -m scripts.load_complaints        # needs entities; --max-per-entity 20 --per-year 3 --dry-run
python -m scripts.load_recalls           # needs entities; --dry-run
```

- Only entities in `monthly_features` are created. Complaints and recalls for other groups are rejected as "no matching entity".
- Complaints: per entity, up to `--per-year` per calendar year (crash/fire/injury/death first, then most recent), then at most `--max-per-entity` in total, picked round-robin across years so every period has excerpts. The text is read only for the selected complaints.
- Complaints and recalls are a full replace of `source='nhtsa'` rows: rows no longer selected are removed.
- `--dry-run` reports what would be loaded without writing.

### Mock data

`python -m scripts.seed_mock` loads `app/mock_data.py` with `source='mock'` (negative complaint IDs) so the API works before real data exists. It refuses to run once real data is loaded. `python -m scripts.seed_mock --clear` removes it.

## Tests

```bash
python -m pytest
```

Tests use `DIRECT_DATABASE_URL` in a throwaway schema `rr_test_<random>`, dropped at the end even when a test fails. Sample files are generated in a temporary directory and deleted afterwards. Without a database URL the DB tests are skipped.
