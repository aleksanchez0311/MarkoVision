#!/bin/bash
# MarkoVision Production Startup Script
# ========================================
# Script para iniciar el servidor de producción

# Detectar SO
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    PORT=${PORT:-8050}
    echo "========================================"
    echo "MarkoVision - Production Server (Windows)"
    echo "========================================"
    echo "Puerto: $PORT"
    echo ""
    
    # Usar waitress en Windows
    waitress-serve --host=0.0.0.0 --port=$PORT --threads=6 wsgi:app
else
    # Linux/Mac
    PORT=${PORT:-8050}
    echo "========================================"
    echo "MarkoVision - Production Server (Linux)"
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

    # Iniciar servidor con Gunicorn (mejores prestaciones en Linux)
    exec gunicorn \
        --workers 4 \
        --bind 0.0.0.0:$PORT \
        --timeout 120 \
        --access-logfile - \
        --error-logfile - \
        wsgi:app
fi
