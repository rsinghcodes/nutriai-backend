from fastapi import APIRouter, Request, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from db.session import get_db
from db.models.food import FoodItem, FoodLog
from schemas.food_log import FoodLogCreate, FoodLogResponse, FoodSummaryResponse, DailyFoodSummary
from datetime import datetime, timedelta

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
def list_food_logs(
    request: Request,
    date: str = Query(None, description="Filter logs for a specific date (YYYY-MM-DD)")
):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db: Session = next(get_db())

    query = (
        db.query(FoodLog, FoodItem)
        .join(FoodItem, FoodItem.id == FoodLog.food_id)
        .filter(FoodLog.user_id == user.id)
    )

    # ✅ If date filter provided, restrict logs to that day
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        day_start = datetime.combine(target_date, datetime.min.time())
        day_end = day_start + timedelta(days=1)

        query = query.filter(
            FoodLog.logged_at >= day_start,
            FoodLog.logged_at < day_end
        )
    
    logs = query.order_by(FoodLog.logged_at.desc()).all()

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

@router.get("/summary", response_model=FoodSummaryResponse)
def get_food_summary(
    request: Request,
    days: int = 7,
    db: Session = Depends(get_db)
):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    today = datetime.utcnow().date()
    since_date = today - timedelta(days=days - 1)

    daily_logs = (
        db.query(
            func.date(FoodLog.logged_at).label("date"),
            func.sum(FoodItem.calories * (FoodLog.quantity / FoodItem.reference_amount)).label("calories"),
            func.sum(FoodItem.protein * (FoodLog.quantity / FoodItem.reference_amount)).label("protein"),
            func.sum(FoodItem.carbs * (FoodLog.quantity / FoodItem.reference_amount)).label("carbs"),
            func.sum(FoodItem.fats * (FoodLog.quantity / FoodItem.reference_amount)).label("fats"),
        )
        .join(FoodItem, FoodItem.id == FoodLog.food_id)
        .filter(
            FoodLog.user_id == user.id,
            FoodLog.logged_at >= since_date
        )
        .group_by(func.date(FoodLog.logged_at))
        .order_by(func.date(FoodLog.logged_at).desc())
        .all()
    )

    daily_summary = [
        DailyFoodSummary(
            date=row.date,
            calories=float(row.calories or 0),
            protein=float(row.protein or 0),
            carbs=float(row.carbs or 0),
            fats=float(row.fats or 0),
        )
        for row in daily_logs
    ]

    return FoodSummaryResponse(
        days=days,
        range_start=since_date,
        range_end=today,
        total_calories=sum(d.calories for d in daily_summary),
        total_protein=sum(d.protein for d in daily_summary),
        total_carbs=sum(d.carbs for d in daily_summary),
        total_fats=sum(d.fats for d in daily_summary),
        daily=daily_summary
    )