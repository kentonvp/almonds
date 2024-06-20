import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine(os.environ["DB_URL"], echo=True)
SessionLocal = sessionmaker(engine)


class Base(DeclarativeBase):
    pass
