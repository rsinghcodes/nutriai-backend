from pydantic import BaseModel
from typing import List

class FoodResponse(BaseModel):
    id: int
    name: str
    calories: float
    protein: float
    carbs: float
    fats: float
    reference_amount: float
    reference_unit: str

    class Config:
        from_attributes = True


class PaginatedFoodResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[FoodResponse]
