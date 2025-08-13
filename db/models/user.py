from sqlalchemy import Column, Integer, Text, DECIMAL, JSON, TIMESTAMP
from sqlalchemy.sql import func
from . import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    email = Column(Text, unique=True, index=True)
    password = Column(Text, nullable=False)  # bcrypt hashed
    height_cm = Column(DECIMAL(5, 2))
    weight_kg = Column(DECIMAL(5, 2))
    age = Column(Integer)
    gender = Column(Text)
    bmi = Column(DECIMAL(5, 2))
    dietary_prefs = Column(JSON)
    goals = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
