from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime
from app.db.session import Base


class PulseScore(Base):
    __tablename__ = "pulse_scores"

    id = Column(Integer, primary_key=True)
    iso3 = Column(String(3), ForeignKey("countries.iso3"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    composite_score = Column(Float, nullable=False)
    sentiment_score = Column(Float)
    conflict_score = Column(Float)
    trend = Column(String(20))

    __table_args__ = (UniqueConstraint("iso3", "timestamp"),)
