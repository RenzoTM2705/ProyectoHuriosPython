"""Contrato base para repositorios.

Se usa como punto de extensión para futuras implementaciones con PostgreSQL,
Supabase o cualquier otra fuente de datos.
"""

from abc import ABC


class BaseRepository(ABC):
    """Clase base para repositorios de la capa de infraestructura."""
