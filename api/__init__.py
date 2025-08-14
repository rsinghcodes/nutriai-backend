from fastapi import APIRouter

# Create a global API router
api_router = APIRouter()

# Import and include individual routers
from auth.routes import router as auth_router

# Register routes with their own sub-prefixes
api_router.include_router(auth_router, tags=["Authentication"])
