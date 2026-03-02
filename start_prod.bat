@echo off
REM MarkoVision Production Startup Script (Windows)
REM ================================================
REM Script para iniciar el servidor de producción con Waitress en Windows

set PORT=%PORT%
if "%PORT%"=="" set PORT=8050

echo ========================================
echo MarkoVision - Production Server
echo ========================================
echo Puerto: %PORT%
echo.

REM Verificar que waitress esté instalado
waitress-serve --version >nul 2>&1
if errorlevel 1 (
    echo Advertencia: waitress no esta instalado
    echo Instalando...
    pip install waitress
)

REM Iniciar servidor con Waitress
echo Iniciando servidor de produccion...
waitress-serve --host=0.0.0.0 --port=%PORT% --threads=6 wsgi:app
