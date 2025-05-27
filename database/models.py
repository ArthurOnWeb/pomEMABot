# database/models.py

from sqlalchemy import Column, Integer, String, UniqueConstraint
from database.connection import Base

class Pair(Base):
    __tablename__ = "pairs"
    __table_args__ = (
        UniqueConstraint("chat_id", "symbol", "timeframe", name="uq_pair"),
    )

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True, nullable=False)
    symbol = Column(String, index=True, nullable=False)
    timeframe = Column(String, default="1h", nullable=False)
