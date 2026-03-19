from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib
import time
import json
import base64

router = APIRouter(prefix="/auth")

# Demo users (matches frontend Login.jsx)
USERS = [
    {"email": "anushtha@ornatesolar.in",     "password": "Admin@1234",    "name": "Anushtha",        "role": "admin",      "organisation": "Ornate Solar"},
    {"email": "fateh@ornatesolar.com",        "password": "Admin@1234",    "name": "Fateh Brar",      "role": "admin",      "organisation": "Ornate Solar"},
    {"email": "kedar@ornatesolar.com",        "password": "Admin@1234",    "name": "Kedar Bala",      "role": "admin",      "organisation": "Ornate Solar"},
    {"email": "ravi.sharma@ornatesolar.com",  "password": "Ornate@1234",   "name": "Ravi Sharma",     "role": "engineer",   "organisation": "Ornate Solar"},
    {"email": "priya.nair@ornatesolar.com",   "password": "Ornate@1234",   "name": "Priya Nair",      "role": "reviewer",   "organisation": "Ornate Solar"},
    {"email": "arun.mehta@ornatesolar.com",   "password": "Ornate@1234",   "name": "Arun Mehta",      "role": "commercial", "organisation": "Ornate Solar"},
    {"email": "vijay.k@sunsure.in",           "password": "Customer@1234", "name": "Vijay Kumar",     "role": "customer",   "organisation": "SunSure Energy"},
]


class LoginRequest(BaseModel):
    email: str
    password: str


def _make_token(user: dict) -> str:
    """Create a simple base64 JWT-like token (dev mode, not production-safe)."""
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload_data = {
        "sub": f"user-{hashlib.md5(user['email'].encode()).hexdigest()[:8]}",
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "org": user["organisation"],
        "iat": int(time.time()),
        "exp": int(time.time()) + 8 * 3600,
    }
    payload = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(
        hashlib.sha256(f"{header}.{payload}.dev-secret".encode()).digest()
    ).decode().rstrip("=")
    return f"{header}.{payload}.{signature}"


@router.post("/login")
async def login(body: LoginRequest):
    user = next(
        (u for u in USERS if u["email"].lower() == body.email.lower() and u["password"] == body.password),
        None,
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = _make_token(user)
    return {
        "token": token,
        "user": {
            "id": f"user-{hashlib.md5(user['email'].encode()).hexdigest()[:8]}",
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "organisation": user["organisation"],
        },
    }


@router.get("/me")
async def me():
    return {"message": "Use token to identify user"}
