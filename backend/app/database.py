"""
Kết nối database và SQLAlchemy session.
Hỗ trợ cả SQLite (local) và PostgreSQL (Railway).
"""
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings


def _sqlite_path() -> str:
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        current = os.path.dirname(os.path.abspath(__file__))
        # app/ -> backend/ -> project root
        base = os.path.dirname(os.path.dirname(current))
    return os.path.join(base, "shop.db")


def _build_database_url() -> str:
    url = settings.DATABASE_URL
    if not url:
        return f"sqlite:///{_sqlite_path()}"
    # Railway injekts postgres:// nhưng SQLAlchemy cần postgresql://
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return url


DATABASE_URL = _build_database_url()
IS_SQLITE = DATABASE_URL.startswith("sqlite")

connect_args = {"check_same_thread": False} if IS_SQLITE else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency: cung cấp DB session cho mỗi request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
