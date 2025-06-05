# database/models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, UniqueConstraint
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


class PriceAlert(Base):
    __tablename__ = "price_alerts"
    __table_args__ = (
        UniqueConstraint("chat_id", "symbol", "target_price", name="uq_price_alert"),
    )

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True, nullable=False)
    symbol = Column(String, index=True, nullable=False)
    target_price = Column(Float, nullable=False)
    direction = Column(String, nullable=False)
    active = Column(Boolean, default=True, nullable=False)


