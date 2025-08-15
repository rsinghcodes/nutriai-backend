from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal
from enum import Enum

class GenderType(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class DietaryPreference(str, Enum):
    veg = "veg"
    non_veg = "non-veg"
    vegan = "vegan"

class GoalType(str, Enum):
    weight_loss = "weight loss"
    weight_gain = "weight gain"
    maintain_healthy = "maintain healthy"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserOnboarding(BaseModel):
    age: int
    gender: Literal["male", "female", "other"]
    height_cm: float
    weight_kg: float
    dietary_prefs: Optional[List[DietaryPreference]] = None
    goals: Optional[GoalType] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AuthUser(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_onboarded: bool
    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    message: str
    user: AuthUser
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    age: int | None
    gender: str | None
    height_cm: float | None
    weight_kg: float | None
    bmi: float | None
    dietary_prefs: Optional[List[DietaryPreference]]
    goals: Optional[GoalType]
    is_onboarded: bool

    class Config:
        from_attributes = True
