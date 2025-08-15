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

    # Determine total units performed
    if workout.unit == "reps":
        total_reps = body.sets * body.reps_per_set
    elif workout.unit == "minutes":
        total_reps = body.duration_minutes
    else:
        raise HTTPException(status_code=400, detail="Unsupported workout unit")

    # Auto-calculate calories
    estimated_calories = float(workout.calories_per_unit) * total_reps

    workout_log = WorkoutLog(
        user_id=user.id,
        workout_id=workout.id,
        sets=body.sets if workout.unit == "reps" else None,
        reps_per_set=body.reps_per_set if workout.unit == "reps" else None,
        total_reps=total_reps,
        estimated_calories=estimated_calories
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
        total_reps=total_reps ,
        estimated_calories=estimated_calories,
        muscle_groups=workout.muscle_groups,
        logged_at=workout_log.logged_at
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
        if workout.unit == "reps":
            total_reps = log.sets * log.reps_per_set
        elif workout.unit == "minutes":
            total_reps = log.duration_minutes
        else:
            total_reps = None

        results.append(
            WorkoutLogResponse(
                id=log.id,
                workout_id=workout.id,
                workout_name=workout.name,
                unit=workout.unit,
                sets=log.sets,
                reps_per_set=log.reps_per_set,
                total_reps=total_reps,
                estimated_calories=log.estimated_calories,
                muscle_groups=workout.muscle_groups,
                logged_at=log.logged_at
            )
        )

    return results
