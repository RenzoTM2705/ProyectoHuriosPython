"""Utilidades centralizadas para JWT.

La emisión y validación del token se concentran aquí para que el resto de la
aplicación solo consuma una interfaz sencilla y consistente.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError

from app.config.settings import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Crea un JWT de acceso firmado con el secreto configurado."""

    payload = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))

    payload.update(
        {
            "exp": expire,
            "iat": now,
            "type": "access",
        }
    )

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Decodifica y valida la firma del JWT."""

    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"verify_aud": False},
        )
    except ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token es inválido",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return claims


def verify_token(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    """Verifica el token y valida las reclamaciones mínimas esperadas."""

    claims = decode_token(token)

    if claims.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token no es válido para acceso",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = claims.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token no contiene un sujeto válido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return claims
