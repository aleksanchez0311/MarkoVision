@echo off
REM MarkoVision Production Startup Script (Windows)
REM ================================================
REM Script para iniciar el servidor de producción con Gunicorn en Windows

set PORT=%PORT%
if "%PORT%"=="" set PORT=8050

echo ========================================
echo MarkoVision - Production Server
echo ========================================
echo Puerto: %PORT%
echo Workers: 4
echo.

REM Verificar que gunicorn esté instalado
gunicorn --version >nul 2>&1
if errorlevel 1 (
    echo Error: gunicorn no esta instalado
    echo Instala con: pip install gunicorn
    pause
    exit /b 1
)

REM Iniciar servidor con Gunicorn
echo Iniciando servidor de produccion...
gunicorn --workers 4 --bind 0.0.0.0:%PORT% --timeout 120 wsgi:app
