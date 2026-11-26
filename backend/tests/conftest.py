import uuid

import pytest

from app.db.models import Base
from app.db.session import database_url, make_engine
from scripts.load_common import DB_TABLES


@pytest.fixture(scope="session")
def engine():
    """Engine bound to a throwaway schema rr_test_<random>, always dropped afterwards."""
    try:
        url = database_url(direct=True)
    except RuntimeError:
        pytest.skip("DIRECT_DATABASE_URL / DATABASE_URL not set")

    schema = f"rr_test_{uuid.uuid4().hex[:8]}"
    admin = make_engine(url)
    test_engine = make_engine(url, search_path=schema)
    try:
        with admin.begin() as conn:
            conn.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
        Base.metadata.create_all(test_engine)
        yield test_engine
    finally:
        test_engine.dispose()
        with admin.begin() as conn:
            conn.exec_driver_sql(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
        admin.dispose()


@pytest.fixture
def db(engine):
    with engine.begin() as conn:
        conn.exec_driver_sql(f"TRUNCATE {', '.join(DB_TABLES)} RESTART IDENTITY CASCADE")
    return engine
