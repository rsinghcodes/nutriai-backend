from fastapi import APIRouter

# Create a global API router
api_router = APIRouter()

# Import and include individual routers
from auth.routes import router as auth_router
from api.food_logs import router as food_log
from api.workout_logs import router as workout_log
from api.plans import router as generate_ai_plan

# Register routes with their own sub-prefixes
api_router.include_router(auth_router, tags=["Authentication"])
api_router.include_router(food_log, tags=["Food Logs"])
api_router.include_router(workout_log, tags=["Workout Logs"])
api_router.include_router(generate_ai_plan, tags=["Generate AI Plan"])