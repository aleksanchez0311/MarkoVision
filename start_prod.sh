#!/bin/bash
# MarkoVision Production Startup Script
# ========================================
# Script para iniciar el servidor de producción con Gunicorn

# Configurar puerto (default: 8050)
PORT=${PORT:-8050}

echo "========================================"
echo "MarkoVision - Production Server"
echo "========================================"
echo "Puerto: $PORT"
echo "Workers: 4"
echo ""

# Verificar que gunicorn esté instalado
if ! command -v gunicorn &> /dev/null; then
    echo "Error: gunicorn no está instalado"
    echo "Instala con: pip install gunicorn"
    exit 1
fi

# Iniciar servidor con Gunicorn
# Esto elimina el warning de desarrollo
exec gunicorn \
    --workers 4 \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    wsgi:app
