# MarkovLens Pro - Especificaciones del Proyecto

## Descripción

Aplicación de análisis de mercado que implementa un Modelo Oculto de Markov (HMM) para la detección de regímenes de mercado con visualización interactiva.

## Componentes Principales

### 1. Módulo de Datos y Feature Engineering (`data_generator.py`)

- Generador de datos OHLCV mock con patrones de mercado realistas
- Cálculo de características multidimensionales:
  - **Retornos logarítmicos**: ln(Close*t / Close*{t-1})
  - **Volatilidad**: ATR normalizado o desviación estándar móvil de 14 períodos
  - **Momentum**: Pendiente de SMA(20) o RSI(14)
- Soporte para múltiples timeframes: 5m, 15m, 1h, 4h, 1d

### 2. Modelo HMM (`hmm_model.py`)

- Implementación con GaussianHMM de hmmlearn
- Parámetros configurables:
  - n_components: 3 a 7 regímenes (seleccionable por usuario)
  - covariance_type: 'full' para mayor flexibilidad
  - n_iter: 100 iteraciones de entrenamiento
- Métodos para predicción y clasificación de estados

### 3. Dashboard Visual (`dashboard.py`)

- Framework: Plotly Dash
- Componentes:
  - Gráfico de velas japonesas (Candlestick)
  - Fondo sombreado por régimen de mercado
  - Colores de regímenes:
    - Verde/Azul: Alcista/Fuerte
    - Gris: Lateral
    - Rojo/Naranja: Bajista/Débil
  - Dropdowns para Timeframe (5m, 15m, 1h, 4h, 1d)
  - Slider/Input para número de regímenes (3-7)
  - Estadísticas del modelo HMM

### 4. Aplicación Principal (`app.py`)

- Integración de todos los módulos
- Interfaz de usuario interactiva
- Actualización en tiempo real de los análisis

## Dependencias

- pandas
- numpy
- plotly
- dash
- hmmlearn
- yfinance (opcional, para datos reales)

## Timeframes Soportados

- 5 minutos (5m)
- 15 minutos (15m)
- 1 hora (1h)
- 4 horas (4h)
- 1 día (1d)

## Regímenes de Mercado

- Configurable entre 3 y 7 estados
- Por defecto: 4 regímenes
  - 0: Tendencia bajista fuerte
  - 1: Mercado lateral/ruidoso
  - 2: Tendencia alcista moderada
  - 3: Tendencia alcista fuerte
