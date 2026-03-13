from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from datetime import datetime
from app.db.session import Base


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True)
    external_id = Column(String(255), unique=True)
    iso3 = Column(String(3), ForeignKey("countries.iso3"))
    title = Column(Text, nullable=False)
    summary = Column(Text)
    url = Column(String(1024))
    sentiment = Column(Float)
    published_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)
