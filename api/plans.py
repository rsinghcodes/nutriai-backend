from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.plan import Plan, PlanItem
from db.models.food import FoodItem

router = APIRouter(
    prefix="/v1/plans",
    tags=["Plans"]
)

@router.get("/")
def get_plans(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    plans = db.query(Plan).filter(Plan.user_id == current_user.id).all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "created_at": p.created_at,
        }
        for p in plans
    ]


@router.get("/{plan_id}")
def get_plan(plan_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user

    # Fetch plan
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Fetch items with food details
    plan_items = (
        db.query(PlanItem, FoodItem)
        .join(FoodItem, PlanItem.food_id == FoodItem.id)
        .filter(PlanItem.plan_id == plan.id)
        .all()
    )

    # Group items into meals by name
    meals_dict = {}
    for item, food in plan_items:
        if item.meal_name not in meals_dict:
            meals_dict[item.meal_name] = []
        meals_dict[item.meal_name].append({
            "food_id": food.id,
            "food_name": food.name,
            "quantity": float(item.quantity),
            "unit": item.unit,
            "calories": float(food.calories),
            "protein": float(food.protein),
            "carbs": float(food.carbs),
            "fats": float(food.fats)
        })

    meals = [{"meal": meal_name, "items": items} for meal_name, items in meals_dict.items()]

    return {
        "plan_id": plan.id,
        "name": plan.name,
        "description": plan.description,
        "meals": meals
    }
