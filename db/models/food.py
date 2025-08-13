from sqlalchemy import Column, Integer, Text, DECIMAL, JSON, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from . import Base

class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    calories = Column(DECIMAL(8, 2))  # per reference amount
    protein = Column(DECIMAL(8, 2))
    carbs = Column(DECIMAL(8, 2))
    fats = Column(DECIMAL(8, 2))
    vitamins = Column(JSON)
    reference_amount = Column(DECIMAL(6, 2), nullable=False)  # e.g., 100.00
    reference_unit = Column(Text, nullable=False)             # e.g., g, piece
    unit_conversions = Column(JSON)                           # {"piece": 40, "cup": 150}

class FoodLog(Base):
    __tablename__ = "food_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_id = Column(Integer, ForeignKey("food_items.id"))
    quantity = Column(DECIMAL(6, 2), nullable=False)
    unit = Column(Text, nullable=False)
    logged_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
