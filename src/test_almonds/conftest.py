import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from almonds.db.base import Base


@pytest.fixture(scope="function")
def sessionmaker_test():
    engine = create_engine("sqlite:///:memory:")
    # Create tables
    Base.metadata.create_all(engine)

    SessionTest = sessionmaker(bind=engine)

    yield SessionTest

    Base.metadata.drop_all(engine)
