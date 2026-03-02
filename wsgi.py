"""
MarkoVision - WSGI Entry Point
==============================
Archivo de entrada WSGI para ejecutar el dashboard en producción.
Uso con Waitress (Windows/Linux):
  waitress-serve --host=0.0.0.0 --port=$PORT wsgi:app
Uso con Gunicorn (Linux):
  gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app

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


# Crear aplicación Dash y obtener el servidor Flask
def create_app():
    """Crea y retorna la aplicación WSGI (servidor Flask de Dash)."""
    from dashboard import MarketDashboard

    dashboard = MarketDashboard()
    # Dash proporciona acceso al servidor Flask subyacente mediante app.server
    return dashboard.app.server


# Aplicación WSGI
app = create_app()

# Configuración de producción
if __name__ != "__main__":
    logger.info("MarkoVision iniciando en modo producción con WSGI")

# Para ejecutar directamente con waitress:
# waitress-serve --host=0.0.0.0 --port=8050 wsgi:app
