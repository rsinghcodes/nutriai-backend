from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class WorkoutLogCreate(BaseModel):
    workout_id: int
    sets: Optional[int] = None
    reps_per_set: Optional[int] = None
    duration_minutes: Optional[int] = None

class WorkoutLogResponse(BaseModel):
    id: int
    workout_id: int
    workout_name: str
    unit: str
    sets: Optional[int]
    reps_per_set: Optional[int]
    total_reps: Optional[int]
    estimated_calories: float
    muscle_groups: List[str]
    logged_at: datetime

    class Config:
        from_attributes = True
