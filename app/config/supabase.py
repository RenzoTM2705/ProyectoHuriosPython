"""Cliente de Supabase centralizado.

La conexión se resuelve una sola vez y se reutiliza en toda la aplicación.
Si faltan variables de entorno, se expone un error explícito para fallar rápido
y evitar errores silenciosos en tiempo de ejecución.
"""

from functools import lru_cache

from supabase import Client, create_client

from app.config.settings import settings


class SupabaseConfigError(RuntimeError):
    """Señala que la configuración de Supabase es incompleta o inválida."""


@lru_cache
def get_supabase_client() -> Client:
    """Crea y reutiliza un cliente oficial de Supabase para toda la app."""

    if not settings.supabase_url or not settings.supabase_key:
        raise SupabaseConfigError(
            "Supabase no está configurado. Define SUPABASE_URL y SUPABASE_KEY."
        )

    return create_client(settings.supabase_url, settings.supabase_key)
