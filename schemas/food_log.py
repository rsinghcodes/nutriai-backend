from pydantic import BaseModel, condecimal
from datetime import datetime
from decimal import Decimal
from typing import Annotated

class FoodLogCreate(BaseModel):
    food_id: int
    quantity: Annotated[Decimal, condecimal(gt=0)]  # in given unit
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
