# auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt
import uuid
import os

router = APIRouter()
security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserRegister(BaseModel):
    email: str
    password: str
    business_name: str
    plan: str = "small"

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str
    business_name: str

# Simple in-memory storage (replace with database)
users = []

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", response_model=TokenResponse)
async def register(user: UserRegister):
    # Check if user exists
    for existing in users:
        if existing["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    hashed = hash_password(user.password)
    
    new_user = {
        "id": user_id,
        "email": user.email,
        "hashed_password": hashed,
        "business_name": user.business_name,
        "plan": user.plan,
        "created_at": datetime.utcnow().isoformat()
    }
    users.append(new_user)
    
    access_token = create_access_token(data={"sub": user.email, "user_id": user_id})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user_id,
        email=user.email,
        business_name=user.business_name
    )

@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    # Find user
    found_user = None
    for u in users:
        if u["email"] == user.email:
            found_user = u
            break
    
    if not found_user or not verify_password(user.password, found_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email, "user_id": found_user["id"]})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=found_user["id"],
        email=found_user["email"],
        business_name=found_user["business_name"]
    )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id, "email": payload.get("sub")}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
