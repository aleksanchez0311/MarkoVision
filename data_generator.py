"""
Módulo de Generación de Datos y Feature Engineering
=====================================================
Este módulo proporciona funciones para generar datos OHLCV mock
y calcular características para el modelo HMM.

Autor: MarkoVision
Fecha: 2026
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional
from datetime import datetime, timedelta


class MarketDataGenerator:
    """
    Generador de datos de mercado con patrones realistas.
    Simula diferentes regímenes de mercado: tendencia alcista, bajista y lateral.
    """

    def __init__(self, seed: int = 42):
        """
        Inicializa el generador de datos.

        Args:
            seed: Semilla para reproducibilidad de resultados aleatorios
        """
        self.seed = seed
        np.random.seed(seed)

    def generate_ohlcv(
        self,
        n_bars: int = 500,
        timeframe: str = "1h",
        initial_price: float = 100.0,
        volatility: float = 0.02,
    ) -> pd.DataFrame:
        """
        Genera datos OHLCV con cambios de régimen integrados.

        Args:
            n_bars: Número de velas a generar
            timeframe: Timeframe ('5m', '15m', '1h', '4h', '1d')
            initial_price: Precio inicial
            volatility: Volatilidad base

        Returns:
            DataFrame con datos OHLCV
        """
        # Mapear timeframes a minutos
        tf_minutes = {"5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}
        minutes = tf_minutes.get(timeframe, 60)

        # Generar fechas
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=minutes * n_bars)
        dates = pd.date_range(start=start_time, periods=n_bars, freq=f"{minutes}min")

        # Generar regímenes de mercado (cambios suaves)
        regime_changes = np.random.choice(
            [0, 1, 2],  # 0: bajista, 1: lateral, 2: alcista
            size=n_bars,
            p=[0.2, 0.4, 0.4],
        )

        # Suavizar cambios de régimen
        regime_smoothed = self._smooth_regimes(regime_changes, window=20)

        # Parámetros por régimen
        regime_params = {
            0: {"drift": -0.001, "vol_mult": 1.5},  # Bajista
            1: {"drift": 0.0001, "vol_mult": 1.0},  # Lateral
            2: {"drift": 0.001, "vol_mult": 1.2},  # Alcista
        }

        # Generar precios
        close_prices = [initial_price]
        high_prices = [initial_price]
        low_prices = [initial_price]

        for i in range(1, n_bars):
            regime = regime_smoothed[i]
            params = regime_params[regime]

            # Retorno aleatorio con deriva del régimen
            daily_return = np.random.normal(
                params["drift"], volatility * params["vol_mult"]
            )

            new_close = close_prices[-1] * (1 + daily_return)

            # Generar high/low realista
            hl_range = (
                new_close
                * volatility
                * params["vol_mult"]
                * np.random.uniform(0.5, 1.5)
            )
            high = new_close + np.random.uniform(0, hl_range)
            low = new_close - np.random.uniform(0, hl_range)

            close_prices.append(new_close)
            high_prices.append(high)
            low_prices.append(low)

        close_prices = np.array(close_prices)
        high_prices = np.array(high_prices)
        low_prices = np.array(low_prices)

        # Generar OHLC
        opens = np.roll(close_prices, 1)
        opens[0] = initial_price * np.random.uniform(0.98, 1.02)

        # Generar volumen
        base_volume = 1000000
        volumes = base_volume * (1 + np.abs(np.random.randn(n_bars) * 0.3))

        # Crear DataFrame
        df = pd.DataFrame(
            {
                "Open": opens,
                "High": high_prices,
                "Low": low_prices,
                "Close": close_prices,
                "Volume": volumes.astype(int),
            },
            index=dates,
        )

        df.index.name = "Date"

        return df

    def _smooth_regimes(self, regimes: np.ndarray, window: int = 20) -> np.ndarray:
        """
        Suaviza los cambios de régimen usando media móvil.

        Args:
            regimes: Array de regímenes
            window: Ventana de suavizado

        Returns:
            Array de regímenes suavizados
        """
        smoothed = np.copy(regimes)
        for i in range(window, len(regimes)):
            smoothed[i] = int(np.round(np.mean(regimes[i - window : i + 1])))
        return smoothed


class FeatureEngineer:
    """
    Ingeniero de características para el modelo HMM.
    Calcula retornos, volatilidad y momentum.
    """

    def __init__(self):
        """Inicializa el ingeniero de características."""
        pass

    def calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula todas las características para el HMM.

        Args:
            df: DataFrame con datos OHLCV

        Returns:
            DataFrame con características calculadas
        """
        features = pd.DataFrame(index=df.index)

        # 1. Retornos logarítmicos
        features["log_return"] = np.log(df["Close"] / df["Close"].shift(1))

        # 2. Volatilidad (ATR normalizado y desviación estándar móvil)
        features["atr"] = self._calculate_atr(df)
        features["atr_normalized"] = features["atr"] / df["Close"]

        features["volatility"] = df["Close"].pct_change().rolling(window=14).std()

        # 3. Momentum
        features["momentum_slope"] = self._calculate_momentum_slope(df)
        features["rsi"] = self._calculate_rsi(df)

        # Normalizar características
        features_normalized = self._normalize_features(features)

        # Eliminar NaN
        features_normalized = features_normalized.dropna()

        return features_normalized

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calcula el Average True Range (ATR).

        Args:
            df: DataFrame con datos OHLCV
            period: Período de cálculo

        Returns:
            Serie con ATR
        """
        high = df["High"]
        low = df["Low"]
        close = df["Close"]

        # True Range
        tr1 = high - low
        tr2 = np.abs(high - close.shift(1))
        tr3 = np.abs(low - close.shift(1))

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        return atr

    def _calculate_momentum_slope(
        self, df: pd.DataFrame, period: int = 20
    ) -> pd.Series:
        """
        Calcula la pendiente de la media móvil (momentum).

        Args:
            df: DataFrame con datos OHLCV
            period: Período de la media móvil

        Returns:
            Serie con pendientes normalizadas
        """
        sma = df["Close"].rolling(window=period).mean()

        # Calcular pendiente como porcentaje
        slope = sma.pct_change(periods=period)

        return slope

    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calcula el Relative Strength Index (RSI).

        Args:
            df: DataFrame con datos OHLCV
            period: Período de cálculo

        Returns:
            Serie con RSI (0-100)
        """
        delta = df["Close"].diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _normalize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza las características usando z-score.

        Args:
            df: DataFrame con características

        Returns:
            DataFrame con características normalizadas
        """
        normalized = df.copy()

        for col in df.columns:
            mean = df[col].mean()
            std = df[col].std()

            if std > 0:
                normalized[col] = (df[col] - mean) / std
            else:
                normalized[col] = 0

        return normalized


def generate_market_data(
    n_bars: int = 500, timeframe: str = "1h", n_regimes: int = 4
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Función principal para generar datos de mercado y características.

    Args:
        n_bars: Número de barras
        timeframe: Timeframe
        n_regimes: Número de regímenes (para compatibilidad)

    Returns:
        Tupla (datos OHLCV, características)
    """
    # Generar datos
    generator = MarketDataGenerator(seed=42)
    ohlcv_data = generator.generate_ohlcv(
        n_bars=n_bars, timeframe=timeframe, initial_price=100.0, volatility=0.02
    )

    # Calcular características
    engineer = FeatureEngineer()
    features = engineer.calculate_features(ohlcv_data)

    return ohlcv_data, features


# Ejemplo de uso
if __name__ == "__main__":
    print("=" * 60)
    print("MARKOVISION - Generador de Datos de Mercado")
    print("=" * 60)

    # Generar datos para diferentes timeframes
    timeframes = ["5m", "15m", "1h", "4h", "1d"]

    for tf in timeframes:
        print(f"\nGenerando datos para timeframe: {tf}")
        ohlcv, features = generate_market_data(n_bars=200, timeframe=tf)
        print(f"  OHLCV shape: {ohlcv.shape}")
        print(f"  Features shape: {features.shape}")
        print(f"  Columnas de features: {list(features.columns)}")

    print("\n" + "=" * 60)
    print("Generación de datos completada exitosamente!")
    print("=" * 60)
