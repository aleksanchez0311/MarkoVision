"""
Dashboard Visual Interactivo - MarkovLens Pro
==============================================
Panel de visualización con gráficos de velas y regímenes de mercado.

Autor: MarkovLens Pro
Fecha: 2026
"""

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import warnings
from functools import lru_cache
from data_generator import generate_market_data
from hmm_model import train_hmm_model

warnings.filterwarnings("ignore")


class MarketDashboard:
    """
    Dashboard interactivo para visualización de regímenes de mercado.
    """

    def __init__(self):
        """Inicializa el dashboard."""
        self.app = dash.Dash(__name__, title="MarkovLens Pro", update_title=None)

        self._setup_layout()
        self._setup_callbacks()

    def _setup_layout(self):
        """Configura el layout de la aplicación con un diseño premium."""

        self.app.layout = html.Div(
            [
                # Custom Premium Global Loader (Visible via CSS when Dash is loading)
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(className="loader-ring"),
                                html.Div(className="loader-ring"),
                                html.Div("MV", className="loader-logo"),
                            ],
                            className="loader-container",
                        ),
                        html.Div(
                            "Calculando Regímenes...",
                            className="loading-text",
                        ),
                    ],
                    className="loading-overlay",
                    id="premium-loader",
                ),
                html.Div(
                    [
                        # Encabezado Premium
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H1("MARKOVLENS PRO"),
                                        html.P(
                                            "Análisis Predictivo de Regímenes de Mercado con HMM",
                                        ),
                                    ],
                                    className="title-group",
                                ),
                            ],
                            className="app-header",
                        ),
                        # Panel de Controles
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label("Activo"),
                                        dcc.Dropdown(
                                            id="symbol-selector",
                                            options=[
                                                {"label": "BTC/USD", "value": "BTCUSD"},
                                                {"label": "ETH/USD", "value": "ETHUSD"},
                                                {"label": "EUR/USD", "value": "EURUSD"},
                                                {
                                                    "label": "SPY (S&P 500)",
                                                    "value": "SPY",
                                                },
                                            ],
                                            value="BTCUSD",
                                            clearable=False,
                                        ),
                                    ],
                                    className="control-item",
                                    style={"width": "25%"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Temporalidad"),
                                        dcc.Dropdown(
                                            id="timeframe-selector",
                                            options=[
                                                {
                                                    "label": "5m (Intradía)",
                                                    "value": "5m",
                                                },
                                                {"label": "15m", "value": "15m"},
                                                {
                                                    "label": "1h (Estándar)",
                                                    "value": "1h",
                                                },
                                                {"label": "4h", "value": "4h"},
                                                {"label": "1d (Swing)", "value": "1d"},
                                            ],
                                            value="1h",
                                            clearable=False,
                                        ),
                                    ],
                                    className="control-item",
                                    style={"width": "25%"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Complejidad (Regímenes)"),
                                        dcc.Dropdown(
                                            id="regimes-selector",
                                            options=[
                                                {"label": "3 - Simple", "value": 3},
                                                {
                                                    "label": "4 - Equilibrado",
                                                    "value": 4,
                                                },
                                                {"label": "5 - Detallado", "value": 5},
                                                {"label": "6 - Complejo", "value": 6},
                                            ],
                                            value=4,
                                            clearable=False,
                                        ),
                                    ],
                                    className="control-item",
                                    style={"width": "25%"},
                                ),
                                # Badge de Estado
                                html.Div(
                                    id="market-status-badge",
                                    className="control-item",
                                    style={"width": "25%"},
                                ),
                            ],
                            className="glass-panel sidebar fade-in",
                            style={
                                "display": "flex",
                                "gap": "20px",
                                "alignItems": "center",
                                "justifyContent": "space-between",
                            },
                        ),
                        # Dashboards Main Section
                        html.Div(
                            [
                                # Main Charts and Sidebar Info
                                html.Div(
                                    [
                                        # Center Chart
                                        html.Div(
                                            [
                                                dcc.Graph(
                                                    id="candlestick-chart",
                                                    className="chart-container",
                                                    config={"displayModeBar": False},
                                                )
                                            ],
                                            className="glass-panel fade-in",
                                            style={"flex": "7"},
                                        ),
                                        # Right Statistics
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.H4("Métricas del Modelo"),
                                                        html.Div(id="model-info"),
                                                    ],
                                                    className="glass-panel stat-card",
                                                    style={"marginBottom": "20px"},
                                                ),
                                                html.Div(
                                                    [
                                                        dcc.Graph(
                                                            id="regime-distribution",
                                                            config={
                                                                "displayModeBar": False
                                                            },
                                                        ),
                                                    ],
                                                    className="glass-panel chart-container",
                                                ),
                                            ],
                                            className="fade-in",
                                            style={
                                                "flex": "3",
                                                "display": "flex",
                                                "flexDirection": "column",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "gap": "25px",
                                        "marginBottom": "25px",
                                    },
                                ),
                                # Bottom Transitions and Matrix
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                dcc.Graph(
                                                    id="transition-matrix",
                                                    config={"displayModeBar": False},
                                                ),
                                            ],
                                            className="glass-panel chart-container",
                                            style={"flex": "1"},
                                        ),
                                    ],
                                    style={"display": "flex", "gap": "25px"},
                                ),
                            ],
                            id="dashboard-content",
                        ),
                        # Footer
                        html.Div(
                            [
                                html.P(
                                    "MARKOVLENS PRO © 2026 | Arquitectura de Inteligencia Financiera Avanzada"
                                )
                            ],
                            className="footer",
                            style={
                                "textAlign": "center",
                                "marginTop": "50px",
                                "opacity": "0.5",
                                "fontSize": "12px",
                                "letterSpacing": "1px",
                            },
                        ),
                    ],
                    className="main-content",
                ),
            ],
            style={"position": "relative"},
        )

    @lru_cache(maxsize=128)
    def _get_processed_data(self, timeframe, n_regimes, symbol):
        """Genera y entrena el modelo de forma optimizada con caché."""
        n_bars = 200 if timeframe in ["5m", "15m"] else 150
        ohlcv, features = generate_market_data(n_bars=n_bars, timeframe=timeframe)
        model, states = train_hmm_model(features, n_components=n_regimes)
        return ohlcv, features, model, states

    def _setup_callbacks(self):
        """Configura los callbacks de la aplicación."""

        @self.app.callback(
            [
                Output("candlestick-chart", "figure"),
                Output("market-status-badge", "children"),
                Output("model-info", "children"),
                Output("regime-distribution", "figure"),
                Output("transition-matrix", "figure"),
            ],
            [
                Input("timeframe-selector", "value"),
                Input("regimes-selector", "value"),
                Input("symbol-selector", "value"),
            ],
        )
        def update_dashboard(timeframe, n_regimes, symbol):
            """Actualiza todos los gráficos automáticamente."""

            # Obtener datos procesados (desde caché si es posible)
            ohlcv, features, model, states = self._get_processed_data(
                timeframe, n_regimes, symbol
            )

            # Obtener información del régimen actual
            current_regime_id, current_regime_info = model.get_current_regime(features)

            # Crear gráfico de velas
            candlestick_fig = self._create_candlestick_chart(ohlcv, states, model)

            # Crear estado del mercado
            status = self._create_market_status(
                symbol, timeframe, current_regime_id, current_regime_info, n_regimes
            )

            # Crear información del modelo
            model_info = self._create_model_info(model, ohlcv, features, states)

            # Crear distribución de regímenes
            distribution_fig = self._create_regime_distribution(states, model)

            # Crear matriz de transición
            transition_fig = self._create_transition_matrix(model)

            return candlestick_fig, status, model_info, distribution_fig, transition_fig

    def _create_candlestick_chart(
        self, ohlcv: pd.DataFrame, states: np.ndarray, model
    ) -> go.Figure:
        """
        Crea el gráfico de velas con fondo sombreado por régimen.

        Args:
            ohlcv: DataFrame con datos OHLCV
            states: Estados predichos por el HMM
            model: Modelo HMM entrenado

        Returns:
            Figura de Plotly
        """
        fig = go.Figure()

        # Crear rectángulos para cada estado
        dates = ohlcv.index

        # Agrupar estados consecutivos
        current_state = states[0]
        start_idx = 0

        for i in range(1, len(states)):
            if states[i] != current_state:
                # Dibujar rectángulo para el estado anterior
                regime_info = model.get_regime_info(current_state)

                fig.add_vrect(
                    x0=dates[start_idx],
                    x1=dates[i - 1],
                    fillcolor=regime_info["color"],
                    opacity=0.15,
                    layer="below",
                    line_width=0,
                )

                current_state = states[i]
                start_idx = i

        # Último rectángulo
        regime_info = model.get_regime_info(current_state)
        fig.add_vrect(
            x0=dates[start_idx],
            x1=dates[-1],
            fillcolor=regime_info["color"],
            opacity=0.15,
            layer="below",
            line_width=0,
        )

        # Añadir gráfico de velas
        fig.add_trace(
            go.Candlestick(
                x=ohlcv.index,
                open=ohlcv["Open"],
                high=ohlcv["High"],
                low=ohlcv["Low"],
                close=ohlcv["Close"],
                name="Precio",
                increasing_line_color="#26A69A",
                decreasing_line_color="#EF5350",
            )
        )

        # Configurar layout premium
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter, sans-serif", "color": "#F8FAFC"},
            xaxis={
                "showgrid": True,
                "gridcolor": "rgba(255,255,255,0.05)",
                "zeroline": False,
                "tickfont": {"size": 10},
            },
            yaxis={
                "showgrid": True,
                "gridcolor": "rgba(255,255,255,0.05)",
                "zeroline": False,
                "tickfont": {"size": 10},
            },
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=500,
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=40),
        )

        return fig

    def _create_market_status(
        self,
        symbol: str,
        timeframe: str,
        regime_id: int,
        regime_info: dict,
        n_regimes: int,
    ) -> html.Div:
        """
        Crea el componente de estado del mercado premium.
        """
        return html.Div(
            [
                html.Span(
                    "STATUS ",
                    style={
                        "fontSize": "10px",
                        "opacity": "0.6",
                        "letterSpacing": "1px",
                    },
                ),
                html.Span(
                    regime_info["name"].upper(),
                    className="status-indicator",
                    style={
                        "backgroundColor": f"{regime_info['color']}33",
                        "color": regime_info["color"],
                        "border": f"1px solid {regime_info['color']}",
                    },
                ),
            ],
            style={"textAlign": "right"},
        )

    def _create_model_info(
        self, model, ohlcv: pd.DataFrame, features: pd.DataFrame, states: np.ndarray
    ) -> html.Div:
        """
        Crea el componente de información del modelo con diseño premium.
        """
        returns = ohlcv["Close"].pct_change().dropna()
        total_return = (ohlcv["Close"].iloc[-1] / ohlcv["Close"].iloc[0] - 1) * 100
        volatility = returns.std() * 100
        sharpe = (
            (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        )

        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.P("Retorno", className="stat-label"),
                                html.H3(
                                    f"{total_return:+.1f}%", className="stat-value"
                                ),
                            ],
                            style={"flex": "1"},
                        ),
                        html.Div(
                            [
                                html.P("Volatilidad", className="stat-label"),
                                html.H3(f"{volatility:.1f}%", className="stat-value"),
                            ],
                            style={"flex": "1"},
                        ),
                    ],
                    style={"display": "flex", "marginBottom": "15px"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P("Sharpe", className="stat-label"),
                                html.H3(f"{sharpe:.2f}", className="stat-value"),
                            ],
                            style={"flex": "1"},
                        ),
                        html.Div(
                            [
                                html.P("Score", className="stat-label"),
                                html.H3(
                                    f"{model.get_model_score(features):.0f}",
                                    className="stat-value",
                                ),
                            ],
                            style={"flex": "1"},
                        ),
                    ],
                    style={"display": "flex"},
                ),
            ]
        )

    def _create_regime_distribution(self, states: np.ndarray, model) -> go.Figure:
        """
        Crea el gráfico de distribución de regímenes.
        """
        unique, counts = np.unique(states, return_counts=True)
        labels = [model.get_regime_info(s)["name"] for s in unique]
        colors = [model.get_regime_info(s)["color"] for s in unique]

        fig = go.Figure(
            data=[
                go.Bar(
                    x=labels,
                    y=counts,
                    marker=dict(
                        color=colors, line=dict(color="rgba(255,255,255,0.1)", width=1)
                    ),
                    text=counts,
                    textposition="auto",
                )
            ]
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter, sans-serif", "color": "#F8FAFC"},
            title={
                "text": "DISTRIBUCIÓN DE ESTADOS",
                "font": {"size": 12, "color": "#94A3B8"},
            },
            template="plotly_dark",
            height=200,
            margin=dict(l=30, r=30, t=50, b=30),
            showlegend=False,
            xaxis={"gridcolor": "rgba(255,255,255,0.05)"},
            yaxis={"gridcolor": "rgba(255,255,255,0.05)"},
        )

        return fig

    def _create_transition_matrix(self, model) -> go.Figure:
        """
        Crea el heatmap de la matriz de transición con diseño premium.
        """
        trans_matrix = model.get_transition_matrix()
        n = trans_matrix.shape[0]
        labels = [f"Reg {i}" for i in range(n)]

        fig = go.Figure(
            data=[
                go.Heatmap(
                    z=trans_matrix,
                    x=labels,
                    y=labels,
                    colorscale=[[0, "#1E293B"], [1, "#00F2FF"]],
                    text=np.round(trans_matrix, 3),
                    texttemplate="%{text}",
                    textfont={"family": "Inter, sans-serif", "size": 11},
                    showscale=False,
                )
            ]
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter, sans-serif", "color": "#F8FAFC"},
            title={
                "text": "MATRIZ DE PROBABILIDAD DE TRANSICIÓN",
                "font": {"size": 12, "color": "#94A3B8"},
            },
            template="plotly_dark",
            height=300,
            margin=dict(l=50, r=50, t=50, b=50),
            xaxis={"side": "bottom"},
        )

        return fig

    def run(self, debug: bool = False, port: int = 8050):
        """
        Inicia el servidor del dashboard.

        Args:
            debug: Modo debug
            port: Puerto del servidor
        """
        self.app.run(debug=debug, port=port, host="0.0.0.0")


# Función de creación del dashboard (para integración)
def create_dashboard():
    """Crea y retorna la instancia del dashboard."""
    return MarketDashboard()


# Ejemplo de uso
if __name__ == "__main__":
    print("=" * 60)
    print("MARKOVLENS PRO - Dashboard")
    print("=" * 60)
    print("\nIniciando servidor del dashboard...")
    print("Accede a: http://127.0.0.1:8050")
    print("\nPresiona Ctrl+C para detener el servidor")
    print("=" * 60)

    dashboard = MarketDashboard()
    dashboard.run(debug=True, port=8050)
