from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.food import FoodItem, FoodLog
from schemas.food_log import FoodLogCreate, FoodLogResponse

router = APIRouter(
    prefix="/v1/food-logs",
    tags=["Food Logs"]
)

@router.post("/", response_model=FoodLogResponse)
def create_food_log(request: Request, body: FoodLogCreate):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db: Session = next(get_db())

    food_item = db.query(FoodItem).filter(FoodItem.id == body.food_id).first()
    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found")

    # Nutrient scaling
    if body.unit == food_item.reference_unit:
        scale_factor = float(body.quantity) / float(food_item.reference_amount)
    else:
        if not food_item.unit_conversions or body.unit not in food_item.unit_conversions:
            raise HTTPException(status_code=400, detail="Invalid unit for this food item")
        converted_qty = float(body.quantity) * float(food_item.unit_conversions[body.unit])
        scale_factor = converted_qty / float(food_item.reference_amount)

    food_log = FoodLog(
        user_id=user.id,
        food_id=food_item.id,
        quantity=body.quantity,
        unit=body.unit
    )
    db.add(food_log)
    db.commit()
    db.refresh(food_log)

    return FoodLogResponse(
        id=food_log.id,
        food_id=food_item.id,
        food_name=food_item.name,
        quantity=float(body.quantity),
        unit=body.unit,
        logged_at=food_log.logged_at,
        calories=float(food_item.calories) * scale_factor,
        protein=float(food_item.protein) * scale_factor,
        carbs=float(food_item.carbs) * scale_factor,
        fats=float(food_item.fats) * scale_factor,
        vitamins={k: v * scale_factor for k, v in (food_item.vitamins or {}).items()}
    )


@router.get("/", response_model=list[FoodLogResponse])
def list_food_logs(request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db: Session = next(get_db())

    logs = (
        db.query(FoodLog, FoodItem)
        .join(FoodItem, FoodItem.id == FoodLog.food_id)
        .filter(FoodLog.user_id == user.id)
        .order_by(FoodLog.logged_at.desc())
        .all()
    )

    results = []
    for log, food in logs:
        if log.unit == food.reference_unit:
            scale_factor = float(log.quantity) / float(food.reference_amount)
        else:
            converted_qty = float(log.quantity) * float(food.unit_conversions.get(log.unit, 0))
            scale_factor = converted_qty / float(food.reference_amount) if food.reference_amount else 0

        results.append(
            FoodLogResponse(
                id=log.id,
                food_id=food.id,
                food_name=food.name,
                quantity=float(log.quantity),
                unit=log.unit,
                logged_at=log.logged_at,
                calories=float(food.calories) * scale_factor,
                protein=float(food.protein) * scale_factor,
                carbs=float(food.carbs) * scale_factor,
                fats=float(food.fats) * scale_factor,
                vitamins={k: v * scale_factor for k, v in (food.vitamins or {}).items()}
            )
        )

    return results
