from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.user import User
from auth.jwt_handler import decode_access_token

class OnboardingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip middleware for public routes
        public_paths = [
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/users/onboarding"
        ]
        if any(path.startswith(pub) for pub in public_paths):
            return await call_next(request)

        # Only check for /api/v1 routes
        if path.startswith("/api/v1/"):
            # Extract token from Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

            token = auth_header.split(" ")[1]

            # Decode JWT to get user_id
            payload = decode_access_token(token)
            if not payload:
                return JSONResponse(status_code=401, content={"detail": "Invalid token"})

            user_id = payload.get("sub")
            if not user_id:
                return JSONResponse(status_code=401, content={"detail": "Invalid token payload"})

            # DB session
            db: Session = next(get_db())
            user = db.query(User).filter(User.id == int(user_id)).first()

            if not user:
                return JSONResponse(status_code=401, content={"detail": "User not found"})

            # Attach user to request.state for downstream use
            request.state.user = user

            # Check onboarding status
            if not user.is_onboarded:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Please complete onboarding before accessing this resource."}
                )

        return await call_next(request)
