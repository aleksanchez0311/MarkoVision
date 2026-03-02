# MarkoVision

**Análisis de Regímenes de Mercado con Modelo Oculto de Markov (HMM)**

---

## Descripción

MarkoVision es una herramienta de análisis cuantitativo que implementa un Modelo Oculto de Markov (GaussianHMM) para la detección automática de regímenes de mercado. La aplicación incluye un dashboard visual interactivo que permite visualizar los diferentes estados del mercado en gráficos de velas.

## Características Principales

- **Modelo HMM**: Implementación con GaussianHMM de hmmlearn
- **Selector de Regímenes**: Configurable entre 3 y 7 estados
- **Múltiples Timeframes**: Soporte para 5m, 15m, 1h, 4h, 1d
- **Feature Engineering**: Retornos logarítmicos, volatilidad (ATR), momentum (RSI y pendiente SMA)
- **Dashboard Visual**: Gráficos de velas con fondo sombreado por régimen
- **Interfaz Interactiva**: Dropdowns para timeframe y número de regímenes
- **Loader**: Spinner de carga durante actualizaciones

## Estructura del Proyecto

```
MarkoVision/
├── SPECS.md              # Especificaciones del proyecto
├── README.md             # Este archivo
├── requirements.txt      # Dependencias Python
├── app.py               # Script principal (CLI + Dashboard)
├── data_generator.py    # Generación de datos + Feature Engineering
├── hmm_model.py          # Modelo HMM
├── dashboard.py          # Dashboard visual con Plotly Dash
└── assets/
    └── style.css         # Estilos adicionales
```

## Instalación

1. **Clonar o descargar el proyecto**

2. **Instalar dependencias**:

```bash
pip install -r requirements.txt
```

## Uso

### Dashboard Visual (Recomendado)

Inicia el dashboard interactivo:

```bash
python app.py --dashboard
```

Accede a: `http://127.0.0.1:8050`

### Análisis CLI

Ejecuta un análisis por línea de comandos:

```bash
python app.py --analyze --timeframe 1h --regimes 4
```

### Demostración

Ejecuta una demostración rápida:

```bash
python app.py --demo
```

## Parámetros

### Parámetros del Dashboard

| Parámetro | Descripción               | Opciones                    |
| --------- | ------------------------- | --------------------------- |
| Timeframe | Temporalidad del análisis | 5m, 15m, 1h, 4h, 1d         |
| Regímenes | Número de estados HMM     | 3, 4, 5, 6, 7               |
| Símbolo   | Activo a analizar         | BTCUSD, ETHUSD, EURUSD, SPY |

### Parámetros CLI

```bash
python app.py --help

# Opciones:
#   --demo              Ejecutar demostración
#   --dashboard         Iniciar dashboard visual
#   --analyze           Ejecutar análisis CLI
#   --timeframe TF      Timeframe (default: 1h)
#   --regimes N         Número de regímenes (default: 4)
#   --bars N            Número de barras (default: 200)
#   --symbol S          Símbolo (default: BTCUSD)
#   --port N            Puerto del dashboard (default: 8050)
```

## Feature Engineering

El modelo HMM se entrena con características multidimensionales:

1. **Retornos Logarítmicos**: `ln(Close_t / Close_{t-1})`
2. **Volatilidad**:
   - ATR (Average True Range) normalizado
   - Desviación estándar móvil (14 períodos)
3. **Momentum**:
   - Pendiente de SMA(20)
   - RSI(14)

## Regímenes de Mercado

La aplicación detecta y clasifica los siguientes regímenes:

| Régimen           | Color         | Descripción                            |
| ----------------- | ------------- | -------------------------------------- |
| Caída Fuerte      | Rojo Intenso  | Tendencia bajista con alta volatilidad |
| Tendencia Bajista | Rojo          | Movimiento descendente                 |
| Mercado Lateral   | Gris          | Consolidación sin tendencia clara      |
| Alta Vol. Alcista | Verde Azulado | Subida con volatilidad                 |
| Tendencia Alcista | Azul          | Movimiento ascendente                  |

## Matriz de Transición

El dashboard muestra la matriz de transición de probabilidades, que indica la probabilidad de pasar de un régimen a otro en cada paso de tiempo.

## Tecnologías

- **Python 3.8+**
- **pandas** - Manipulación de datos
- **numpy** - Operaciones numéricas
- **hmmlearn** - Implementación de HMM
- **plotly** - Visualización interactiva
- **dash** - Framework del dashboard

## Acceso desde Red Local

El servidor está configurado para aceptar conexiones desde cualquier dirección IP:

- **Local**: http://127.0.0.1:8050
- **Red local**: http://[TU-IP-LOCAL]:8050

## Licencia

© 2026 MarkoVision - Todos los derechos reservados.

## Notas

- Los datos de mercado son simulados (mock data) para propósitos de demostración
- Para datos reales, se puede integrar yfinance o ccxt
- El modelo HMM requiere un mínimo de datos para un entrenamiento efectivo
