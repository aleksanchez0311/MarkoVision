"""
MarkoVision - WSGI Entry Point
==============================
Archivo de entrada WSGI para ejecutar el dashboard en producción.
Uso con Gunicorn: gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app

Autor: MarkoVision
Fecha: 2026
"""

import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Crear aplicación Dash
def create_app():
    """Crea y configura la aplicación Dash."""
    from dashboard import MarketDashboard

    dashboard = MarketDashboard()
    return dashboard.app


# Aplicación WSGI
app = create_app()

# Configuración de producción
if __name__ != "__main__":
    logger.info("MarkoVision iniciando en modo producción con WSGI")
