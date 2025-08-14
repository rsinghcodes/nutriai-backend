from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
