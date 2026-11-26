"""Create all tables. Run from backend/: python -m app.db.init_db"""
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from app.db.models import Base
from app.db.session import get_direct_engine


def init_db(engine: Engine) -> list[str]:
    Base.metadata.create_all(engine, checkfirst=True)
    return sorted(inspect(engine).get_table_names())


if __name__ == "__main__":
    tables = init_db(get_direct_engine())
    print("Tables:", ", ".join(tables))
