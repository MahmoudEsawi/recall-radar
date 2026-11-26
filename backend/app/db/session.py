import os
from functools import lru_cache
from pathlib import Path
from typing import Iterator, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

SessionLocal = sessionmaker(autoflush=False, expire_on_commit=False)


def _normalize_url(url: str) -> str:
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def database_url(direct: bool = False) -> str:
    """Pooled URL for the API; direct URL (falls back to pooled) for scripts and tests."""
    url = os.getenv("DIRECT_DATABASE_URL") if direct else None
    url = url or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Copy backend/.env.example to backend/.env.")
    return _normalize_url(url)


def make_engine(url: str, pooled: bool = False, search_path: Optional[str] = None) -> Engine:
    # PgBouncer in transaction mode can't keep server-side prepared statements
    connect_args = {"prepare_threshold": None} if pooled else {}
    engine = create_engine(url, pool_pre_ping=True, connect_args=connect_args)

    if search_path:
        @event.listens_for(engine, "connect", insert=True)
        def _set_search_path(dbapi_connection, _record):
            autocommit = dbapi_connection.autocommit
            dbapi_connection.autocommit = True
            with dbapi_connection.cursor() as cur:
                cur.execute(f'SET SESSION search_path TO "{search_path}"')
            dbapi_connection.autocommit = autocommit

    return engine


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return make_engine(database_url(), pooled=True)


@lru_cache(maxsize=1)
def get_direct_engine() -> Engine:
    return make_engine(database_url(direct=True))


def get_db() -> Iterator[Session]:
    """FastAPI dependency."""
    db = SessionLocal(bind=get_engine())
    try:
        yield db
    finally:
        db.close()
