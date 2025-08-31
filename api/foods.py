from fastapi import APIRouter, Depends, Query
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.food import FoodItem
from typing import Optional
from schemas.FoodResponse import PaginatedFoodResponse

router = APIRouter(
    prefix="/v1/foods", 
    tags=["Foods"]
)

@router.get("/", response_model=PaginatedFoodResponse)
def list_foods(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search food items by name"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    sort_by: str = Query("name", description="Sort field: name, calories, protein, carbs, fats"),
    order: str = Query("asc", description="Order: asc or desc"),

    # New macro filters
    min_calories: Optional[float] = Query(None),
    max_calories: Optional[float] = Query(None),
    min_protein: Optional[float] = Query(None),
    max_protein: Optional[float] = Query(None),
    min_carbs: Optional[float] = Query(None),
    max_carbs: Optional[float] = Query(None),
    min_fats: Optional[float] = Query(None),
    max_fats: Optional[float] = Query(None),
):
    query = db.query(FoodItem)

    if search:
        query = query.filter(FoodItem.name.ilike(f"%{search}%"))

    # Apply macro filters
    if min_calories is not None:
        query = query.filter(FoodItem.calories >= min_calories)
    if max_calories is not None:
        query = query.filter(FoodItem.calories <= max_calories)

    if min_protein is not None:
        query = query.filter(FoodItem.protein >= min_protein)
    if max_protein is not None:
        query = query.filter(FoodItem.protein <= max_protein)

    if min_carbs is not None:
        query = query.filter(FoodItem.carbs >= min_carbs)
    if max_carbs is not None:
        query = query.filter(FoodItem.carbs <= max_carbs)

    if min_fats is not None:
        query = query.filter(FoodItem.fats >= min_fats)
    if max_fats is not None:
        query = query.filter(FoodItem.fats <= max_fats)

    # Sorting
    sort_field_map = {
        "name": FoodItem.name,
        "calories": FoodItem.calories,
        "protein": FoodItem.protein,
        "carbs": FoodItem.carbs,
        "fats": FoodItem.fats,
    }
    sort_column = sort_field_map.get(sort_by, FoodItem.name)
    query = query.order_by(asc(sort_column) if order == "asc" else desc(sort_column))

    # Pagination
    total = query.count()
    foods = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": foods,
    }
