from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Config ───────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "resumeai-super-secret-key-change-in-prod")
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ─── MongoDB connection ───────────────────────────
client     = AsyncIOMotorClient(MONGO_URL)
db         = client["resumebuilder"]
users_col  = db["users"]

# ─── JWT helpers ───────────────────────────────────────
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

# ─── Async user operations (MongoDB) ─────────────────────
async def create_user(full_name: str, email: str, password: str) -> Optional[dict]:
    """Create a new user. Returns None if email already exists."""
    existing = await users_col.find_one({"email": email})
    if existing:
        return None
    user = {
        "full_name":       full_name,
        "email":           email,
        "hashed_password": hash_password(password),
        "created_at":      datetime.utcnow().isoformat(),
    }
    await users_col.insert_one(user)
    return {"full_name": user["full_name"], "email": user["email"]}

async def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Validate credentials. Returns user dict or None."""
    user = await users_col.find_one({"email": email})
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return {"full_name": user["full_name"], "email": user["email"]}

async def get_user_by_email(email: str) -> Optional[dict]:
    user = await users_col.find_one({"email": email})
    if user:
        return {"full_name": user["full_name"], "email": user["email"]}
    return None

async def ensure_indexes():
    """Create unique index on email field."""
    await users_col.create_index("email", unique=True)
