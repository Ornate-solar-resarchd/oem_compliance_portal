"""
AuthService — authentication, password hashing, and JWT token creation.

NOTE: The users table in schema.sql does NOT yet have a `password_hash` column.
A migration is required:
    ALTER TABLE users ADD COLUMN password_hash TEXT;
This service assumes the column exists at runtime.
"""
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.base import BaseService

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

_TOKEN_EXPIRY_HOURS = 8


class AuthService(BaseService):
    """Handles credential verification, JWT issuance, and password utilities."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def authenticate(self, email: str, password: str) -> dict:
        """
        Look up user by email, verify bcrypt hash, enforce is_active.

        Returns a plain dict with user fields on success.
        Raises HTTPException (401 for bad creds, 403 for disabled account).
        """
        clean_email = email.lower().strip()

        result = await self.db.execute(
            text(
                """
                SELECT id::text, email, full_name, role::text,
                       organisation, password_hash, is_active
                FROM users
                WHERE email = :email
                """
            ),
            {"email": clean_email},
        )
        row = result.fetchone()

        if not row or not row.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if not self.verify_password(password, row.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if not row.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account disabled",
            )

        return {
            "id": row.id,
            "email": row.email,
            "name": row.full_name,
            "role": row.role,
            "organisation": row.organisation,
        }

    @staticmethod
    def create_access_token(
        user_id: str,
        email: str,
        name: str,
        role: str,
        org: str | None,
    ) -> str:
        """Build and sign a JWT (HS256, 8-hour expiry)."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "email": email,
            "name": name,
            "role": role,
            "org": org or "",
            "exp": now + timedelta(hours=_TOKEN_EXPIRY_HOURS),
            "iat": now,
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def hash_password(plain: str) -> str:
        """Return a bcrypt hash of the plaintext password."""
        return _pwd_ctx.hash(plain)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """Verify a plaintext password against a bcrypt hash."""
        return _pwd_ctx.verify(plain, hashed)
