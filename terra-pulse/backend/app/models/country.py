from sqlalchemy import Column, String, BigInteger, Float
from app.db.session import Base


class Country(Base):
    __tablename__ = "countries"

    iso3 = Column(String(3), primary_key=True)
    iso2 = Column(String(2), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    capital = Column(String(255))
    region = Column(String(100))
    subregion = Column(String(100))
    population = Column(BigInteger)
    latitude = Column(Float)
    longitude = Column(Float)
    currency_code = Column(String(10))
    flag_url = Column(String(512))
