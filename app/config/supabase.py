"""Cliente de Supabase centralizado.

Se deja desacoplado para que la aplicación pueda arrancar aun cuando las
variables de entorno no estén configuradas. En tiempo de ejecución, el cliente
se crea solo cuando realmente se necesita.
"""

from functools import lru_cache

from supabase import Client, create_client

from app.config.settings import settings


@lru_cache
def get_supabase_client() -> Client:
    """Crea un cliente reutilizable de Supabase.

    Se fuerza una validación explícita para evitar errores silenciosos cuando
    falten credenciales.
    """

    if not settings.supabase_url or not settings.supabase_key:
        raise RuntimeError(
            "Supabase no está configurado. Define SUPABASE_URL y SUPABASE_KEY."
        )

    return create_client(settings.supabase_url, settings.supabase_key)
