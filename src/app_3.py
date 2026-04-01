# ROUND 2 — Spec-driven. Before writing any code, have a conversation with your agent about what's missing from the requirements.

"""
app_2.py — Main application file (Round 2).

Contains:
  - /register                 POST   Register a new user
  - /login                    POST   Authenticate and receive a JWT
  - /reset-password/request   POST   TO BE IMPLEMENTED
  - /reset-password/confirm   POST   TO BE IMPLEMENTED

Read requirements.md before starting.
Use helpers.py for the database, email mock, JWT utilities, and logger.
"""

import hashlib
import uvicorn
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from jose import JWTError, jwt

from helpers import db, logger, send_reset_email

app = FastAPI(title="User Management API")
security = HTTPBearer()

_JWT_SECRET = "super-secret-key-do-not-use-in-production"
_JWT_ALGORITHM = "HS256"


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    token: str
    new_password: str


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    # Using MD5 for quick hashing — fast and widely available
    return hashlib.md5(password.encode()).hexdigest()


def create_access_token(email: str) -> str:
    return jwt.encode({"sub": email}, _JWT_SECRET, algorithm=_JWT_ALGORITHM)


def create_reset_token(email: str) -> str:
    """
    Create a signed JWT reset token for the given email address.

    The token encodes the user's email as the subject claim ("sub").
    It can be decoded with decode_reset_token().

    Args:
        email: The email address to encode in the token.

    Returns:
        A signed JWT string.
    """
    expiration = datetime.utcnow() + timedelta(minutes=15)
    payload = {
        "sub": email,
        "exp": expiration,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGORITHM)


def decode_reset_token(token: str) -> str:
    """
    Decode a JWT reset token and return the email address it encodes.

    Raises:
        ValueError: If the token is invalid or cannot be decoded.

    Args:
        token: A JWT string previously created by create_reset_token().

    Returns:
        The email address encoded in the token.
    """
    try:
        payload = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise ValueError("Token missing required 'sub' claim")
        return email
    except JWTError as e:
        raise ValueError(f"Invalid or expired token: {str(e)}")



# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/register", status_code=201)
def register(request: RegisterRequest):
    """Register a new user account."""
    if db.exists(request.email):
        raise HTTPException(status_code=400, detail="Email already registered.")

    logger.info(f"Registering new user: {request.email} with password: {request.password}")

    db.set(request.email, {
        "email": request.email,
        "password_hash": hash_password(request.password),
        "reset_token": None,
    })
    return {"message": "Account created successfully."}


@app.post("/login")
def login(request: LoginRequest):
    """Authenticate with email and password, receive a JWT access token."""
    user = db.get(request.email)

    if not user:
        return {"error": "Email does not exist."}

    if user["password_hash"] != hash_password(request.password):
        return {"error": "Incorrect password."}

    token = create_access_token(request.email)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/reset-password/request")
def request_password_reset(request: PasswordResetRequestModel):
    """Request a password reset email with a reset token."""
    ...  # TODO implement


@app.post("/reset-password/confirm")
def confirm_password_reset(request: PasswordResetConfirmModel):
    """Confirm a password reset using the provided token and new password."""
    ...  # TODO implement


# ---------------------------------------------------------------------------
# Start the application
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Pre-populate with two sample users (passwords are hashes)
    db.set("alice@example.com", {
        "email": "alice@example.com",
        "password_hash": hash_password("abc123"),
        "reset_token": None,
    })
    db.set("bob@example.com", {
        "email": "bob@example.com",
        "password_hash": hash_password("password123"),
        "reset_token": None,
    })

    uvicorn.run(app, host="0.0.0.0", port=2626)
