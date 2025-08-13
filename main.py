from fastapi import FastAPI
from db.base import get_connection
from auth.hashing import hash_password
from auth.jwt_handler import create_access_token

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok", "message": "NutriAI backend running 🚀"}

@app.post("/test-auth")
def test_auth():
    hashed = hash_password("mypassword")
    token = create_access_token({"sub": "user@example.com"})
    return {"hashed_password": hashed, "jwt_token": token}

@app.get("/test-db")
def test_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT version();")
    result = cur.fetchone()
    conn.close()
    return {"db_version": result}
