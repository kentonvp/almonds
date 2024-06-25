import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine(os.environ.get("DB_URL", "sqlite:///:memory:"), echo=True)
SessionLocal = sessionmaker(engine)


class Base(DeclarativeBase):
    pass
