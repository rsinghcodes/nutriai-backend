from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.food import FoodLog, FoodItem
from db.models.workout import WorkoutLog, Workout
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from pytz import timezone

router = APIRouter(
    prefix="/v1/dashboard",
    tags=["Dashboard"]
)

@router.get("/summary")
def get_dashboard_summary(
    request: Request,
    days: int = 7,
    db: Session = Depends(get_db)
):
    current_user = request.state.user
    since_date = datetime.utcnow() - timedelta(days=days)

    # ---- Calories Consumed ----
    food_logs = (
        db.query(
            func.sum(
                (FoodLog.quantity / FoodItem.reference_amount) * FoodItem.calories
            ).label("total_calories"),
            func.sum(
                (FoodLog.quantity / FoodItem.reference_amount) * FoodItem.protein
            ).label("total_protein"),
            func.sum(
                (FoodLog.quantity / FoodItem.reference_amount) * FoodItem.carbs
            ).label("total_carbs"),
            func.sum(
                (FoodLog.quantity / FoodItem.reference_amount) * FoodItem.fats
            ).label("total_fats"),
        )
        .join(FoodItem, FoodLog.food_id == FoodItem.id)
        .filter(FoodLog.user_id == current_user.id, FoodLog.logged_at >= since_date)
        .first()
    )

    # ---- Calories Burned ----
    workout_logs = (
        db.query(
            func.sum(
                (WorkoutLog.duration / Workout.reference_duration) * Workout.calories_burned
            ).label("total_burned")
        )
        .join(Workout, WorkoutLog.workout_id == Workout.id)
        .filter(WorkoutLog.user_id == current_user.id, WorkoutLog.logged_at >= since_date)
        .first()
    )

    consumed = float(food_logs.total_calories or 0)
    burned = float(workout_logs.total_burned or 0)

    return {
        "days": days,
        "calories": {
            "consumed": consumed,
            "burned": burned,
            "net": consumed - burned
        },
        "macros": {
            "protein": float(food_logs.total_protein or 0),
            "carbs": float(food_logs.total_carbs or 0),
            "fats": float(food_logs.total_fats or 0),
        }
    }

@router.get("/trends")
def get_dashboard_trends(
    request: Request,
    days: int = 7,
    db: Session = Depends(get_db)
):
    current_user = request.state.user
    user_tz = timezone("Asia/Kolkata")  # IST
    
    # Get today in user's timezone
    today_local = datetime.now(user_tz).replace(hour=0, minute=0, second=0, microsecond=0)

    since_date = today_local - timedelta(days=days - 1)

    trends = []

    for i in range(days):
        day_start = since_date + timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        # ---- Calories Consumed ----
        food_logs = (
            db.query(
                func.sum(
                    (FoodLog.quantity / FoodItem.reference_amount) * FoodItem.calories
                ).label("calories")
            )
            .select_from(FoodLog)  
            .join(FoodItem, FoodLog.food_id == FoodItem.id)
            .filter(
                FoodLog.user_id == current_user.id,
                FoodLog.logged_at >= day_start,
                FoodLog.logged_at < day_end
            )
            .first()
        )

        # ---- Calories Burned (using estimated_calories) ----
        workout_logs = (
            db.query(
                func.sum(WorkoutLog.estimated_calories).label("burned")
            )
            .filter(
                WorkoutLog.user_id == current_user.id,
                WorkoutLog.logged_at >= day_start,
                WorkoutLog.logged_at < day_end
            )
            .first()
        )

        consumed = float(food_logs.calories or 0)
        burned = float(workout_logs.burned or 0)

        trends.append({
            "date": day_start.date().isoformat(),
            "consumed": consumed,
            "burned": burned,
            "net": consumed - burned
        })

    return {
        "days": days,
        "trends": trends
    }