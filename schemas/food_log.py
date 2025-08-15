from pydantic import BaseModel, condecimal
from datetime import datetime

class FoodLogCreate(BaseModel):
    food_id: int
    quantity: condecimal(gt=0)  # in given unit
    unit: str

class FoodLogResponse(BaseModel):
    id: int
    food_id: int
    food_name: str
    quantity: float
    unit: str
    logged_at: datetime
    calories: float
    protein: float
    carbs: float
    fats: float
    vitamins: dict

    class Config:
        from_attributes = True
