from fastapi import FastAPI
from db.base import get_connection
from auth.hashing import hash_password
from auth.jwt_handler import create_access_token
from core.middleware import AuthAndOnboardingMiddleware

from api import api_router

app = FastAPI(title="NutriAI Backend")

app.add_middleware(AuthAndOnboardingMiddleware)

# Mount the API router under /api
app.include_router(api_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok", "message": "NutriAI backend running 🚀"}

@app.get("/test-db")
def test_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT version();")
    result = cur.fetchone()
    conn.close()
    return {"db_version": result}
