"""
Módulo del Modelo Oculto de Markov (HMM)
========================================
Implementa un modelo GaussianHMM para detección de regímenes de mercado.

Autor: MarkovLens Pro
Fecha: 2026
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional, List
from hmmlearn.hmm import GaussianHMM
import warnings

# Suprimir warnings de convergencia
warnings.filterwarnings("ignore")


class MarketHMM:
    """
    Modelo Oculto de Markov para detección de regímenes de mercado.

    Utiliza GaussianHMM para identificar diferentes estados del mercado
    basándose en características multidimensionales.
    """

    def __init__(
        self,
        n_components: int = 4,
        covariance_type: str = "full",
        n_iter: int = 100,
        random_state: int = 42,
    ):
        """
        Inicializa el modelo HMM.

        Args:
            n_components: Número de estados/regímenes (3-7)
            covariance_type: Tipo de covarianza ('full', 'tied', 'diag', 'spherical')
            n_iter: Número de iteraciones de entrenamiento
            random_state: Semilla aleatoria para reproducibilidad
        """
        self.n_components = n_components
        self.covariance_type = covariance_type
        self.n_iter = n_iter
        self.random_state = random_state

        self.model = None
        self.is_fitted = False
        self.regime_names = []
        self.regime_colors = []

    def fit(self, features: pd.DataFrame) -> "MarketHMM":
        """
        Entrena el modelo HMM con las características especificadas.

        Args:
            features: DataFrame con características (debe contener las columnas
                     de retornos, volatilidad y momentum)

        Returns:
            Self para encadenamiento de métodos
        """
        # Preparar datos para el modelo
        feature_cols = ["log_return", "volatility", "momentum_slope"]

        # Verificar que existan las columnas necesarias
        available_cols = [col for col in feature_cols if col in features.columns]

        if len(available_cols) < 2:
            # Si faltan columnas, usar todas las disponibles
            X = features.fillna(0).values
        else:
            X = features[available_cols].fillna(0).values

        # Crear y entrenar el modelo
        self.model = GaussianHMM(
            n_components=self.n_components,
            covariance_type=self.covariance_type,
            n_iter=self.n_iter,
            random_state=self.random_state,
            algorithm="viterbi",
        )

        self.model.fit(X)
        self.is_fitted = True

        # Analizar los estados descubiertos
        self._analyze_regimes(features)

        return self

    def _analyze_regimes(self, features: pd.DataFrame) -> None:
        """
        Analiza los regímenes descubiertos y asigna nombres y colores.

        Args:
            features: DataFrame con características
        """
        # Obtener la secuencia de estados más probables
        hidden_states = self.predict(features)

        # Calcular estadísticas por régimen
        regime_stats = []

        for i in range(self.n_components):
            mask = hidden_states == i

            stats = {
                "regime_id": i,
                "mean_return": features["log_return"].iloc[mask].mean()
                if "log_return" in features.columns
                else 0,
                "mean_volatility": features["volatility"].iloc[mask].mean()
                if "volatility" in features.columns
                else 0,
                "count": mask.sum(),
                "probability": mask.sum() / len(hidden_states),
            }

            regime_stats.append(stats)

        # Ordenar regímenes por retorno medio (de peor a mejor)
        regime_stats = sorted(regime_stats, key=lambda x: x["mean_return"])

        # Asignar nombres según las características
        self.regime_mapping = {}
        self.regime_colors = []

        for idx, stats in enumerate(regime_stats):
            regime_id = stats["regime_id"]

            # Clasificar según el retorno y volatilidad (Paleta Premium)
            if stats["mean_return"] < -0.0005:
                if stats["mean_volatility"] > 0.025:
                    name = f"Crash / Pánico ({regime_id})"
                    color = "#FF0055"  # Rosa neón / Rojo pánico
                else:
                    name = f"Distribución / Bajista ({regime_id})"
                    color = "#FF5E5E"  # Rojo suave
            elif stats["mean_return"] > 0.0005:
                if stats["mean_volatility"] > 0.025:
                    name = f"Volatilidad / Exuberancia ({regime_id})"
                    color = "#00F2FF"  # Cyan (Accent Primary)
                else:
                    name = f"Acumulación / Alcista ({regime_id})"
                    color = "#7000FF"  # Violeta (Accent Secondary)
            else:
                name = f"Consolidación / Lateral ({regime_id})"
                color = "#94A3B8"  # Slate (Text Secondary)

            self.regime_mapping[regime_id] = {
                "name": name,
                "color": color,
                "index": idx,
                "stats": stats,
            }
            self.regime_colors.append(color)

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """
        Predice la secuencia de estados más probable.

        Args:
            features: DataFrame con características

        Returns:
            Array con los estados predichos
        """
        if not self.is_fitted:
            raise ValueError("El modelo debe ser entrenado primero")

        feature_cols = ["log_return", "volatility", "momentum_slope"]
        available_cols = [col for col in feature_cols if col in features.columns]

        if len(available_cols) < 2:
            X = features.fillna(0).values
        else:
            X = features[available_cols].fillna(0).values

        return self.model.predict(X)

    def predict_proba(self, features: pd.DataFrame) -> np.ndarray:
        """
        Predice las probabilidades de cada estado.

        Args:
            features: DataFrame con características

        Returns:
            Matriz de probabilidades (n_samples, n_components)
        """
        if not self.is_fitted:
            raise ValueError("El modelo debe ser entrenado primero")

        feature_cols = ["log_return", "volatility", "momentum_slope"]
        available_cols = [col for col in feature_cols if col in features.columns]

        if len(available_cols) < 2:
            X = features.fillna(0).values
        else:
            X = features[available_cols].fillna(0).values

        return self.model.predict_proba(X)

    def get_regime_info(self, regime_id: int) -> dict:
        """
        Obtiene información sobre un régimen específico.

        Args:
            regime_id: ID del régimen

        Returns:
            Diccionario con información del régimen
        """
        if regime_id in self.regime_mapping:
            return self.regime_mapping[regime_id]
        return {"name": "Desconocido", "color": "#888888", "index": regime_id}

    def get_current_regime(self, features: pd.DataFrame) -> Tuple[int, dict]:
        """
        Obtiene el régimen actual del mercado.

        Args:
            features: DataFrame con características

        Returns:
            Tupla (ID del régimen, información del régimen)
        """
        if not self.is_fitted:
            raise ValueError("El modelo debe ser entrenado primero")

        # Usar la última observación
        last_features = features.iloc[-1:].copy()

        regime_id = self.predict(last_features)[0]
        regime_info = self.get_regime_info(regime_id)

        return regime_id, regime_info

    def get_model_score(self, features: pd.DataFrame) -> float:
        """
        Obtiene el score del modelo (log-likelihood).

        Args:
            features: DataFrame con características

        Returns:
            Log-likelihood del modelo
        """
        if not self.is_fitted:
            raise ValueError("El modelo debe ser entrenado primero")

        feature_cols = ["log_return", "volatility", "momentum_slope"]
        available_cols = [col for col in feature_cols if col in features.columns]

        if len(available_cols) < 2:
            X = features.fillna(0).values
        else:
            X = features[available_cols].fillna(0).values

        return self.model.score(X)

    def get_transition_matrix(self) -> np.ndarray:
        """
        Obtiene la matriz de transición de estados.

        Returns:
            Matriz de transición (n_components, n_components)
        """
        if not self.is_fitted:
            raise ValueError("El modelo debe ser entrenado primero")

        return self.model.transmat_

    def get_means(self) -> np.ndarray:
        """
        Obtiene las medias de cada estado.

        Returns:
            Array de medias (n_components, n_features)
        """
        if not self.is_fitted:
            raise ValueError("El modelo debe ser entrenado primero")

        return self.model.means_


def train_hmm_model(
    features: pd.DataFrame, n_components: int = 4, covariance_type: str = "full"
) -> Tuple[MarketHMM, np.ndarray]:
    """
    Función auxiliar para entrenar el modelo HMM.

    Args:
        features: DataFrame con características
        n_components: Número de regímenes (3-7)
        covariance_type: Tipo de covarianza

    Returns:
        Tupla (modelo entrenado, estados predichos)
    """
    # Validar n_components
    n_components = max(3, min(7, n_components))

    # Crear y entrenar el modelo
    model = MarketHMM(
        n_components=n_components,
        covariance_type=covariance_type,
        n_iter=100,
        random_state=42,
    )

    model.fit(features)

    # Predicción de estados
    states = model.predict(features)

    return model, states


def get_regime_statistics(
    ohlcv: pd.DataFrame, features: pd.DataFrame, states: np.ndarray
) -> pd.DataFrame:
    """
    Calcula estadísticas por régimen de mercado.

    Args:
        ohlcv: DataFrame con datos OHLCV
        features: DataFrame con características
        states: Array con estados predichos

    Returns:
        DataFrame con estadísticas por régimen
    """
    stats_list = []

    for regime_id in np.unique(states):
        mask = states == regime_id

        regime_ohlcv = ohlcv[mask]

        stats = {
            "Regimen": regime_id,
            "Frecuencia": mask.sum(),
            "Porcentaje": f"{mask.sum() / len(states) * 100:.1f}%",
            "Return Promedio": f"{regime_ohlcv['Close'].pct_change().mean() * 100:.3f}%",
            "Volatilidad": f"{regime_ohlcv['Close'].pct_change().std() * 100:.2f}%",
            "Precio Inicio": f"${regime_ohlcv['Close'].iloc[0]:.2f}",
            "Precio Fin": f"${regime_ohlcv['Close'].iloc[-1]:.2f}",
        }

        stats_list.append(stats)

    return pd.DataFrame(stats_list)


# Ejemplo de uso
if __name__ == "__main__":
    print("=" * 60)
    print("MARKOVLENS PRO - Modelo HMM")
    print("=" * 60)

    # Importar generador de datos
    from data_generator import generate_market_data

    # Generar datos
    ohlcv, features = generate_market_data(n_bars=500, timeframe="1h")
    print(f"\nDatos generados: {ohlcv.shape}")
    print(f"Features: {features.shape}")

    # Probar diferentes números de regímenes
    for n_reg in [3, 4, 5, 6]:
        print(f"\n--- Entrenando HMM con {n_reg} regímenes ---")

        model, states = train_hmm_model(features, n_components=n_reg)

        print(f"  Log-Likelihood: {model.get_model_score(features):.2f}")
        print(f"  Transiciones únicas: {len(np.unique(states))}")

        # Mostrar información de regímenes
        for i in range(n_reg):
            info = model.get_regime_info(i)
            print(f"  Régimen {i}: {info['name']}")

    print("\n" + "=" * 60)
    print("Modelo HMM entrenado exitosamente!")
    print("=" * 60)
