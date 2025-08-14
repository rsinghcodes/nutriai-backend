from sqlalchemy.orm import Session
from db.session import engine, SessionLocal
from db.models.workout import Workout
from db.models.food import FoodItem

def seed_workouts(session: Session):
    workouts = [
        Workout(name='Push-ups', unit='reps', calories_per_unit=0.35, muscle_groups=['chest', 'triceps', 'shoulders'], difficulty='medium'),
        Workout(name='Squats', unit='reps', calories_per_unit=0.32, muscle_groups=['legs', 'glutes'], difficulty='easy'),
        Workout(name='Jumping Jacks', unit='minutes', calories_per_unit=8.0, muscle_groups=['full body'], difficulty='easy'),
        Workout(name='Surya Namaskar', unit='reps', calories_per_unit=4.0, muscle_groups=['full body', 'yoga'], difficulty='medium'),
        Workout(name='Plank', unit='minutes', calories_per_unit=5.0, muscle_groups=['core', 'abs'], difficulty='medium'),
        Workout(name='Lunges', unit='reps', calories_per_unit=0.35, muscle_groups=['legs', 'glutes'], difficulty='medium'),
        Workout(name='Mountain Climbers', unit='minutes', calories_per_unit=10.0, muscle_groups=['core', 'cardio'], difficulty='hard'),
        Workout(name='Burpees', unit='reps', calories_per_unit=1.0, muscle_groups=['full body'], difficulty='hard'),
        Workout(name='Cycling (indoor)', unit='minutes', calories_per_unit=7.5, muscle_groups=['legs', 'cardio'], difficulty='easy'),
        Workout(name='Yoga (general)', unit='minutes', calories_per_unit=3.0, muscle_groups=['flexibility', 'calm'], difficulty='easy'),
    ]
    for workout in workouts:
        exists = session.query(Workout).filter_by(name=workout.name).first()
        if not exists:
            session.add(workout)
    session.commit()

def seed_food_items(session: Session):
    food_items = [
        FoodItem(name='Chapati', calories=70, protein=2.5, carbs=15, fats=0.5, vitamins={}, reference_amount=40, reference_unit='g', unit_conversions={"piece": 40}),
        FoodItem(name='Rice (cooked)', calories=130, protein=2.7, carbs=28, fats=0.3, vitamins={}, reference_amount=100, reference_unit='g'),
        FoodItem(name='Dal (cooked)', calories=120, protein=9, carbs=20, fats=2, vitamins={}, reference_amount=100, reference_unit='g'),
        FoodItem(name='Paneer', calories=265, protein=18, carbs=1.2, fats=21, vitamins={}, reference_amount=100, reference_unit='g'),
        FoodItem(name='Banana', calories=105, protein=1.3, carbs=27, fats=0.3, vitamins={}, reference_amount=118, reference_unit='g', unit_conversions={"piece": 118}),
        FoodItem(name='Milk', calories=60, protein=3.2, carbs=5, fats=3.25, vitamins={}, reference_amount=100, reference_unit='ml', unit_conversions={"cup": 240}),
    ]
    for food in food_items:
        exists = session.query(FoodItem).filter_by(name=food.name).first()
        if not exists:
            session.add(food)
    session.commit()

def main():
    from db.models import Base  # Ensure models are loaded
    Base.metadata.create_all(bind=engine)  # Create tables if not exist

    with SessionLocal() as session:
        seed_workouts(session)
        seed_food_items(session)
        print("✅ Seed data inserted successfully (idempotent).")

if __name__ == "__main__":
    main()
