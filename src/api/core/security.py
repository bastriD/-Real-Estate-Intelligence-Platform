from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash

from src.api.core.config import settings


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    *,
    subject: str,
    role: str,
    utilisateur_id: int,
    expires_minutes: int | None = None,
) -> str:
    now = datetime.now(timezone.utc)

    expiry_minutes = (
        expires_minutes
        if expires_minutes is not None
        else settings.jwt_access_token_expire_minutes
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "uid": utilisateur_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=expiry_minutes),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )