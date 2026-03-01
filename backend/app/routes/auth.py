from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.services.auth_service import (
    create_user, authenticate_user, create_access_token
)

router = APIRouter()

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest):
    """Register a new user in MongoDB"""
    user = await create_user(req.full_name, req.email, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists."
        )
    return {"message": "Account created successfully."}

@router.post("/login")
async def login(req: LoginRequest):
    """Authenticate user and return JWT token"""
    user = await authenticate_user(req.email, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    token = create_access_token({"sub": user["email"], "name": user["full_name"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "full_name": user["full_name"],
            "email":     user["email"]
        }
    }
