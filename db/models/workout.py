from sqlalchemy import Column, Integer, Text, DECIMAL, ARRAY, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from . import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True)
    unit = Column(Text)
    calories_per_unit = Column(DECIMAL(5, 2))
    muscle_groups = Column(ARRAY(Text))
    difficulty = Column(Text)

class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    workout_id = Column(Integer, ForeignKey("workouts.id"))
    sets = Column(Integer)
    reps_per_set = Column(Integer)
    total_reps = Column(Integer)  # computed in backend, not DB generated
    estimated_calories = Column(DECIMAL(6, 2))
    logged_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
