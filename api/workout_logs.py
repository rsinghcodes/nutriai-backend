from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.workout import Workout, WorkoutLog
from schemas.workout_logs import WorkoutLogCreate, WorkoutLogResponse

router = APIRouter(
    prefix="/v1/workout-logs",
    tags=["Workout Logs"]
)

@router.post("/", response_model=WorkoutLogResponse)
def log_workout(request: Request, body: WorkoutLogCreate):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db: Session = next(get_db())

    workout = db.query(Workout).filter(Workout.id == body.workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    # Strength workouts (reps-based)
    if workout.unit == "reps":
        if body.sets is None or body.reps_per_set is None:
            raise HTTPException(status_code=400, detail="Sets and reps are required for reps-based workout")
        total_reps = body.sets * body.reps_per_set
        duration_minutes = None
        estimated_calories = float(workout.calories_per_unit) * total_reps

    # Time-based workouts (cardio, yoga, etc.)
    elif workout.unit == "minutes":
        if body.duration_minutes is None:
            raise HTTPException(status_code=400, detail="Duration is required for time-based workout")
        total_reps = None
        duration_minutes = body.duration_minutes
        estimated_calories = float(workout.calories_per_unit) * duration_minutes

    else:
        raise HTTPException(status_code=400, detail="Unsupported workout unit")

    workout_log = WorkoutLog(
        user_id=user.id,
        workout_id=workout.id,
        sets=body.sets if workout.unit == "reps" else None,
        reps_per_set=body.reps_per_set if workout.unit == "reps" else None,
        total_reps=total_reps,
        duration_minutes=duration_minutes,
        estimated_calories=estimated_calories,
    )
    db.add(workout_log)
    db.commit()
    db.refresh(workout_log)

    return WorkoutLogResponse(
        id=workout_log.id,
        workout_id=workout.id,
        workout_name=workout.name,
        unit=workout.unit,
        sets=workout_log.sets,
        reps_per_set=workout_log.reps_per_set,
        total_reps=total_reps,
        duration_minutes=duration_minutes,
        estimated_calories=estimated_calories,
        muscle_groups=workout.muscle_groups,
        logged_at=workout_log.logged_at,
    )


@router.get("/", response_model=list[WorkoutLogResponse])
def list_workouts(request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db: Session = next(get_db())

    logs = (
        db.query(WorkoutLog, Workout)
        .join(Workout, Workout.id == WorkoutLog.workout_id)
        .filter(WorkoutLog.user_id == user.id)
        .order_by(WorkoutLog.logged_at.desc())
        .all()
    )

    results = []
    for log, workout in logs:
        results.append(
            WorkoutLogResponse(
                id=log.id,
                workout_id=workout.id,
                workout_name=workout.name,
                unit=workout.unit,
                sets=log.sets,
                reps_per_set=log.reps_per_set,
                total_reps=log.total_reps,
                duration_minutes=log.duration_minutes,  # ⬅️ now properly returned
                estimated_calories=float(log.estimated_calories),
                muscle_groups=workout.muscle_groups,
                logged_at=log.logged_at,
            )
        )

    return results
