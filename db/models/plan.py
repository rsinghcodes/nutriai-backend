from sqlalchemy import Column, Integer, Text, JSON, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.sql import func
from . import Base

class AIPlan(Base):
    __tablename__ = "ai_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_type = Column(Text)
    prompt = Column(Text)
    response = Column(JSON)
    generated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reminder_type = Column(Text)
    message = Column(Text)
    scheduled_at = Column(TIMESTAMP(timezone=True))
    sent = Column(Boolean, default=False)
