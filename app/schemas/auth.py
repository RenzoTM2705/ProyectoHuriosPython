"""Esquemas de autenticación para la API pública."""

import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class AuthCredentialsRequest(BaseModel):
    """Datos requeridos para registro e inicio de sesión."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Valida formato básico de contraseña para mantener una base segura."""

        if not re.search(r"[A-Za-z]", value):
            raise ValueError("La contraseña debe incluir al menos una letra")
        if not re.search(r"\d", value):
            raise ValueError("La contraseña debe incluir al menos un número")
        return value


class AuthTokenResponse(BaseModel):
    """Tokens devueltos por Supabase."""

    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int | None = None


class AuthUserResponse(BaseModel):
    """Usuario autenticado expuesto por la API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    created_at: str | None = None
    confirmed_at: str | None = None


class AuthResponse(BaseModel):
    """Respuesta estándar para registro e inicio de sesión."""

    message: str
    user: AuthUserResponse
    tokens: AuthTokenResponse | None = None
