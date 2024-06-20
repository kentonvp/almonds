from sqlalchemy.schema import Column
from sqlalchemy.types import BLOB, UUID, DateTime, String
from almonds.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True)
    username = Column(String(20), nullable=False)
    password = Column(String(30), nullable=False)
    email = Column(String(320), nullable=False)
    created_at = Column(DateTime(), nullable=False)
    last_updated = Column(DateTime(), nullable=False)
