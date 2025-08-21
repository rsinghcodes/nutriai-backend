# db/models/plan.py
from sqlalchemy import Column, Integer, Text, JSON, ForeignKey, TIMESTAMP, Boolean, DECIMAL
from sqlalchemy.sql import func
from . import Base

class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(Text, nullable=False)
    description = Column(Text)

class PlanItem(Base):
    __tablename__ = "plan_items"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"))
    food_id = Column(Integer, ForeignKey("food_items.id"))
    quantity = Column(DECIMAL(8, 2), nullable=False)
    unit = Column(Text, nullable=False)
    meal_name = Column(Text, nullable=False)

class AIPlan(Base):
    __tablename__ = "ai_plans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_type = Column(Text)                 # e.g., "meal"
    prompt = Column(Text)                    # optional; store if you build it
    response = Column(JSON)                  # store full GeneratedPlanSchema
    generated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reminder_type = Column(Text)
    message = Column(Text)
    scheduled_at = Column(TIMESTAMP(timezone=True))
    sent = Column(Boolean, default=False)
