# MarkoVision - Especificaciones del Proyecto

## Desc

ripción GeneralMarkoVision es una aplicación de análisis de mercados financieros que implementa un Modelo Oculto de Markov (HMM) para la detección de regímenes de mercado, con visualización interactiva mediante dashboard.

## Requisitos Funcionales

### 1. Modelo HMM (GaussianHMM)

- Implementación usando la librería `hmmlearn`
- Número de estados/regímenes configur a 7**
  ables: **3- Tipo de covarianza: `full` para mayor flexibilidad
- Algoritmo: decodificación
  Viterbi para- Iteraciones de entrenamiento: 100

### 2. Selector de Regímenes

- Variable/Parámetro claramente definido en UI
- Dropdown con opciones: 3, 4, 5, 6, 7 regímenes
- Cambio dinámico sin reiniciar la aplicación

### 3. Múltiples Timeframes

Soporte para las siguientes temporalidades:

- **5m** (5 minutos)
- **15m** (15 minutos)
- **1h** (1 hora)
- **4h** (4 horas)
- **1d** (1 día)

### 4. Feature Engineering

El modelo HMM se alimenta de características multidimensionales:

#### 4.1 Retornos Logarítmicos

```
log_return = ln(Close_t / Close_{t-1})
```

#### 4.2 Volatilidad

- **ATR (Average True Range)**: Calculado con período 14, normalizado por el precio de cierre
- **Desviación estándar móvil**: Rolling std con ventana de 14 períodos sobre los retornos

#### 4.3 Momentum

- **Pendiente de SMA**: Pendiente de la media móvil simple de 20 períodos, expresada como porcentaje
- **RSI (Relative Strength Index)**: Calculado con período 14, escala 0-100

#### 4.4 Normalización

Todas las características se normalizan usando z-score (media=0, desviación=1)

## Componentes de la Aplicación

### Módulos Python

| Módulo                                   | Descripción                                          |
| ---------------------------------------- | ---------------------------------------------------- |
| [`data_generator.py`](data_generator.py) | Generación de datos OHLCV mock y cálculo de features |
| [`hmm_model.py`](hmm_model.py)           | Implementación del modelo GaussianHMM                |
| [`dashboard.py`](dashboard.py)           | Dashboard interactivo con Plotly Dash                |
| [`app.py`](app.py)                       | Script principal con CLI                             |

### Dashboard Visual

Componentes del interfaz:

1. **Header**: Título "MarkoVision"
2. **Controles**:
   - Dropdown Timeframe (5m, 15m, 1h, 4h, 1d)
   - Dropdown Regímenes (3-7)
   - Dropdown Símbolo (BTCUSD, ETHUSD, EURUSD, SPY)
   - Botón "Actualizar"
3. **Indicador de estado**: Muestra régimen actual del mercado
4. **Gráfico principal**: Candlestick con fondo sombreado por régimen
5. **Panel de información**: Estadísticas del modelo
6. **Distribución**: Gráfico de barras con frecuencia de regímenes
7. **Matriz de transición**: Heatmap de probabilidades

### Visualización de Regímenes

| Régimen           | Color         | Código Hex |
| ----------------- | ------------- | ---------- |
| Caída Fuerte      | Rojo Intenso  | #FF4444    |
| Tendencia Bajista | Rojo          | #FF6B6B    |
| Mercado Lateral   | Gris          | #95A5A6    |
| Alta Vol. Alcista | Verde Azulado | #4ECDC4    |
| Tendencia Alcista | Azul          | #45B7D1    |

## Dependencias

```
pandas>=1.5.0
numpy>=1.21.0
hmmlearn>=0.2.7
plotly>=5.10.0
dash>=2.9.0
scikit-learn>=1.0.0
scipy>=1.9.0
```

## API del Modelo HMM

### Clase MarketHMM

```python
class MarketHMM:
    def __init__(self, n_components=4, covariance_type='full', n_iter=100, random_state=42)
    def fit(self, features: pd.DataFrame) -> 'MarketHMM'
    def predict(self, features: pd.DataFrame) -> np.ndarray
    def predict_proba(self, features: pd.DataFrame) -> np.ndarray
    def get_regime_info(self, regime_id: int) -> dict
    def get_current_regime(self, features: pd.DataFrame) -> Tuple[int, dict]
    def get_model_score(self, features: pd.DataFrame) -> float
    def get_transition_matrix(self) -> np.ndarray
    def get_means(self) -> np.ndarray
```

## Configuración de Red

El servidor Dash está configurado para aceptar conexiones desde cualquier dirección IP:

- Host: `0.0.0.0`
- Puerto: `8050` (configurable)

## Métricas del Modelo

- **Log-Likelihood**: Medida de bondad del ajuste
- **Matriz de Transición**: Probabilidades de transición entre estados
- **Distribución de Estados**: Frecuencia de cada régimen en los datos

## Limitaciones

1. Los datos de mercado son simulados (mock data)
2. El modelo requiere un mínimo de datos para entrenamiento efectivo
3. El cambio de regímenes no predice movimientos futuros, solo describe el estado actual

## Historial de Versiones

- **v1.0.0** (2026-03-01): Versión inicial
  - Modelo HMM con GaussianHMM
  - Dashboard visual interactivo
  - Soporte para múltiples timeframes
  - Selector de 3-7 regímenes
  - Loader durante actualizaciones
