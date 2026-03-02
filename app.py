"""
MarkovLens Pro - Aplicación Principal
======================================
Script principal para ejecutar el análisis de regímenes de mercado
con Modelo Oculto de Markov.

Autor: MarkovLens Pro
Fecha: 2026
"""

import sys
import argparse
from typing import Optional

# Importar módulos
from data_generator import generate_market_data, MarketDataGenerator, FeatureEngineer
from hmm_model import MarketHMM, train_hmm_model, get_regime_statistics
from dashboard import MarketDashboard


def print_banner():
    """Imprime el banner de la aplicación."""
    banner = """
    =======================================================================
    
    Modelo Oculto de Markov para Deteccion de
    Regimenes de Mercado
    
    ========================================================================
    """
    print(banner)


def run_analysis(
    timeframe: str = "1h", n_regimes: int = 4, n_bars: int = 200, symbol: str = "BTCUSD"
) -> None:
    """
    Ejecuta el análisis de regímenes de mercado.

    Args:
        timeframe: Timeframe a analizar
        n_regimes: Número de regímenes (3-7)
        n_bars: Número de barras a generar
        symbol: Símbolo a analizar
    """
    print(f"\n{'=' * 60}")
    print(f"MarkovLens Pro - Análisis de Mercado")
    print(f"{'=' * 60}")
    print(f"Símbolo: {symbol}")
    print(f"Timeframe: {timeframe}")
    print(f"Número de regímenes: {n_regimes}")
    print(f"Número de barras: {n_bars}")
    print(f"{'=' * 60}\n")

    # Paso 1: Generar datos
    print("📊 Paso 1: Generando datos de mercado...")
    ohlcv, features = generate_market_data(n_bars=n_bars, timeframe=timeframe)
    print(f"   ✓ Datos generados: {len(ohlcv)} velas")
    print(f"   ✓ Features calculadas: {features.shape}")

    # Paso 2: Entrenar modelo HMM
    print("\n[M] Paso 2: Entrenando modelo HMM...")
    model, states = train_hmm_model(features, n_components=n_regimes)
    print(f"   ✓ Modelo entrenado con {n_regimes} estados")
    print(f"   ✓ Log-Likelihood: {model.get_model_score(features):.2f}")

    # Paso 3: Mostrar información de regímenes
    print("\n[E] Regimenes detectados:")
    for i in range(n_regimes):
        info = model.get_regime_info(i)
        count = (states == i).sum()
        pct = count / len(states) * 100
        print(f"   • {info['name']}: {count} barras ({pct:.1f}%)")

    # Paso 4: Análisis del estado actual
    print("\n> Estado actual del mercado:")
    current_regime_id, current_regime_info = model.get_current_regime(features)
    print(f"   • Régimen: {current_regime_info['name']}")
    print(f"   • Color: {current_regime_info['color']}")

    # Paso 5: Matriz de transición
    print("\n~ Matriz de transicion:")
    trans_matrix = model.get_transition_matrix()
    for i in range(n_regimes):
        row = " ".join([f"{x:.3f}" for x in trans_matrix[i]])
        print(f"   Estado {i}: [{row}]")

    # Paso 6: Estadísticas
    print("\n[S] Estadisticas del mercado:")
    returns = ohlcv["Close"].pct_change().dropna()
    total_return = (ohlcv["Close"].iloc[-1] / ohlcv["Close"].iloc[0] - 1) * 100
    volatility = returns.std() * 100
    sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0

    print(f"   • Retorno total: {total_return:.2f}%")
    print(f"   • Volatilidad: {volatility:.2f}%")
    print(f"   • Sharpe Ratio: {sharpe:.2f}")

    print(f"\n{'=' * 60}")
    print("Análisis completado exitosamente!")
    print(f"{'=' * 60}\n")

    return ohlcv, features, model, states


def run_dashboard(port: int = 8050, debug: bool = False) -> None:
    """
    Inicia el dashboard visual.

    Args:
        port: Puerto del servidor
        debug: Modo debug
    """
    print_banner()
    print("\n>> Iniciando MarkovLens Pro Dashboard...")
    print(f"   Puerto: {port}")
    print(f"   Debug: {debug}")
    print(f"\n   Accede a: http://127.0.0.1:{port}")
    print(f"\n   Presiona Ctrl+C para detener\n")

    dashboard = MarketDashboard()
    dashboard.run(debug=debug, port=port)


def run_demo() -> None:
    """Ejecuta una demostración del sistema."""
    print_banner()
    print("\n>> Ejecutando demostracion...\n")

    # Demo con diferentes timeframes
    timeframes = ["15m", "1h", "4h"]

    for tf in timeframes:
        print(f"\n{'=' * 50}")
        print(f"Demo con timeframe: {tf}")
        print(f"{'=' * 50}")

        ohlcv, features = generate_market_data(n_bars=100, timeframe=tf)

        # Entrenar con diferentes números de regímenes
        for n_reg in [3, 5]:
            model, states = train_hmm_model(features, n_components=n_reg)

            current_regime, info = model.get_current_regime(features)

            print(f"\n  >> {n_reg} regimenes:")
            print(f"     Estado actual: {info['name']}")
            print(f"     Log-Likelihood: {model.get_model_score(features):.2f}")

    print("\n" + "=" * 60)
    print(">> Demostracion completada!")
    print("=" * 60)


# Importar numpy para las estadísticas
import numpy as np


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="MarkovLens Pro - Análisis de Regímenes de Mercado con HMM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python app.py --demo              Ejecutar demostración
  python app.py --dashboard        Iniciar dashboard visual
  python app.py --timeframe 1h    Analizar con timeframe 1h
  python app.py --regimes 5        Usar 5 regímenes
  python app.py --analyze          Ejecutar análisis CLI
        """,
    )

    parser.add_argument("--demo", action="store_true", help="Ejecutar demostración")
    parser.add_argument(
        "--dashboard", action="store_true", help="Iniciar dashboard visual"
    )
    parser.add_argument("--analyze", action="store_true", help="Ejecutar análisis CLI")
    parser.add_argument(
        "--timeframe",
        type=str,
        default="1h",
        choices=["5m", "15m", "1h", "4h", "1d"],
        help="Timeframe a analizar (default: 1h)",
    )
    parser.add_argument(
        "--regimes",
        type=int,
        default=4,
        choices=[3, 4, 5, 6, 7],
        help="Número de regímenes (default: 4)",
    )
    parser.add_argument(
        "--bars",
        type=int,
        default=200,
        help="Número de barras a generar (default: 200)",
    )
    parser.add_argument(
        "--symbol",
        type=str,
        default="BTCUSD",
        help="Símbolo a analizar (default: BTCUSD)",
    )
    parser.add_argument(
        "--port", type=int, default=8050, help="Puerto del dashboard (default: 8050)"
    )

    args = parser.parse_args()

    # Mostrar banner
    print_banner()

    # Ejecutar según argumentos
    if args.demo:
        run_demo()
    elif args.dashboard:
        run_dashboard(port=args.port, debug=False)
    elif args.analyze:
        run_analysis(
            timeframe=args.timeframe,
            n_regimes=args.regimes,
            n_bars=args.bars,
            symbol=args.symbol,
        )
    else:
        # Por defecto, mostrar ayuda y ejecutar demo
        print("\n📌 Uso típico:")
        print("   python app.py --dashboard     # Iniciar dashboard visual")
        print("   python app.py --analyze       # Análisis CLI")
        print("   python app.py --demo          # Ver demostración\n")

        # Ejecutar demo por defecto
        run_demo()


if __name__ == "__main__":
    main()
