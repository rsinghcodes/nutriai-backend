from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import models so Alembic sees them
from .user import User
from .food import FoodItem, FoodLog
from .workout import Workout, WorkoutLog
from .plan import AIPlan, Reminder
