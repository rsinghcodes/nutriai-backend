from sqlalchemy import Column, Integer, Boolean, Text, DECIMAL, JSON, TIMESTAMP
from sqlalchemy.sql import func
from . import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    email = Column(Text, unique=True, index=True, nullable=False)
    password = Column(Text, nullable=False)  # bcrypt hashed

    # Onboarding fields
    height_cm = Column(DECIMAL(5, 2), nullable=True)
    weight_kg = Column(DECIMAL(5, 2), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(Text, nullable=True)
    bmi = Column(DECIMAL(5, 2), nullable=True)
    dietary_prefs = Column(JSON, nullable=True)
    goals = Column(Text, nullable=True)
    is_onboarded = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
