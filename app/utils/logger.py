"""Configuración básica de logging para la aplicación.

El objetivo es disponer de una base uniforme para observabilidad desde el inicio.
"""

import logging


def configure_logging() -> None:
    """Configura el nivel y formato del logger raíz."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
